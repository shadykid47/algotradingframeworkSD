import pandas as pd
from pathlib import Path
import definitions as defs
from datetime import datetime as dt
import datetime
import os, glob


def LoadDF(currpath):
    extension = os.path.splitext(currpath)[1]
    my_file = Path(currpath)
    if my_file.exists():
        if extension == ".csv":
            masterdf = pd.read_csv(currpath)
        elif extension == ".pkl":
            masterdf = pd.read_pickle(currpath)
        try:
            try:
                masterdf = masterdf.drop('datetime.1', axis=1)
                masterdf["datetime"] = pd.to_datetime(masterdf["datetime"])
            except :
                masterdf['datetime'] = masterdf['date'] + ' ' + masterdf['time']
                masterdf["datetime"] = pd.to_datetime(masterdf["datetime"])
                
        except: # THIS EXCEPTION OCCURS WHEN BACKTESTING ON LIVE STORED DATA
            masterdf["datetime"] = pd.to_datetime(masterdf["datetime"])
            masterdf.dropna(inplace=True)
            
        masterdf = masterdf.set_index(masterdf['datetime'])
        
    return masterdf

def GetOptionPriceAtomic(masterdf, symbol, type, strikeprice, time, HLOC):
    exp = GetExpiry(masterdf, symbol)
    cst = strikeprice
    cst = int(round(cst / 100, 0) * 100)
    price = 0
    if time in masterdf[masterdf['symbol'] == symbol + exp + str(cst) + type].index.time:
        price = masterdf[masterdf['symbol'] == symbol + exp + str(cst) + type].loc[time][HLOC]
    return price

def GetOptionPrice(masterdf, opsymbol, time, HLOC):
    opdf = masterdf[masterdf['symbol'] == opsymbol]
    if time in opdf.index:
        price = masterdf[masterdf['symbol'] == opsymbol].loc[time][HLOC]
    else:
        price = -1
    return price

def CheckPNL(positions, currentcandle):
    CurrPNL = 0
    for pos in positions:
        if currentcandle.name in pos['OpData'].index:
            if pos["Active"]:
                optionprice = pos["OpData"].loc[currentcandle.name]['open']
                CurrPNL = CurrPNL + pos["PositionConfig"]["Action"] * pos["Qty"]*(optionprice - pos["EnterPrice"])
            else:
                CurrPNL = CurrPNL + pos["trades"]["pnl"]
    return CurrPNL

def GetExpiry(masterdf, symbol):
    if (symbol == defs.BN):
        return masterdf.iloc[0]['symbol'][9:16]
    elif (symbol == defs.N):
        return masterdf.iloc[0]['symbol'][5:12]
    elif symbol == defs.FN:
        return masterdf.iloc[0]['symbol'][8:15]
    else:
        print("Unknown Symbol")
        return 0

def GetNextExpiry(masterdf, symbol):
    if (symbol == defs.BN):
        return masterdf.iloc[0]['symbol'][9:15]
    elif (symbol == defs.N):
        return masterdf.iloc[0]['symbol'][5:11]
    elif symbol == defs.FN:
        return masterdf.iloc[0]['symbol'][8:14]
    else:
        print("Unknown Symbol")
        return 0

def GetSpotData(masterdf, symbol):
    mask1 = masterdf['symbol'] == symbol
    #print(masterdf.info())
    mask2 = masterdf.datetime.dt.time >= datetime.time(9,15)
    df = masterdf[mask1 & mask2]
    df.drop_duplicates(subset=['datetime'], inplace=True)
    return df

def UpdatePosition(masterdf, positions):
    if (len(positions) > 0):
        for pos in positions:
            if (pos["Active"]):
                pos["OpData"] = masterdf[masterdf['symbol'] == pos["OpSymbol"]]
    return positions
    
def EnterPosition(generalconfig, positionconfig, masterdf, positions, currentcandle, OHLC):
    positionsNotPlaced = []
    for posc in positionconfig:
        exp = GetExpiry(masterdf, generalconfig["symbol"])
        if generalconfig['symbol'] == defs.N :
            cst = currentcandle[OHLC]
            cst = int(round(cst / 50, 0)*50)
        elif generalconfig['symbol'] == defs.BN :
            cst = currentcandle[OHLC]
            cst = int(round(cst / 100, 0) * 100)
        elif generalconfig['symbol'] == defs.FN :
            cst = currentcandle[OHLC]
            cst = int(round(cst / 50, 0)*50)
        opdf = masterdf[masterdf['symbol'] == generalconfig["symbol"] + exp + str(cst + posc["Delta"]) + posc["Type"]]
        futdf = masterdf[masterdf['symbol'] == generalconfig['symbol'] + "-I"]
        # print(config["symbol"] + exp + str(cst + pos["Delta"]) + pos["Type"])
        if currentcandle.name in opdf.index:
            price = opdf.loc[currentcandle.name][OHLC]
            try:
                futprice = futdf.loc[currentcandle.name][OHLC]* (1 + generalconfig["Slippage"] * posc["Action"] / 100)
            except:
                futprice = 0
            enterprice = price * (1 + generalconfig["Slippage"] * posc["Action"] / 100)
            position = {"EnterPrice": enterprice, "PositionConfig": posc, "Expiry":exp, "StrikePrice": cst + posc["Delta"],
                "OpSymbol": generalconfig["symbol"] + exp + str(cst + posc["Delta"]) + posc["Type"],
                "FutData": futdf,
                "OpData": masterdf[masterdf['symbol'] == generalconfig["symbol"] + exp + str(cst + posc["Delta"]) + posc["Type"]],
                "Entertime": currentcandle.name.time(), "Qty": generalconfig["LotSize"] * posc["NumLots"],
                "date": currentcandle.name.date(), "EnterSpotPrice": currentcandle[OHLC],
                "SLCond": enterprice*(1 - posc["Action"] * posc["SLPc"] / 100),
                "TargetCond": enterprice + posc["Action"] * enterprice * posc["TargetPc"] / 100,
                "Active": True, "Strike": cst + posc["Delta"],
                "symbol": masterdf.iloc[0]['symbol'], "trades":{}, "Slippage": generalconfig['Slippage'],
                "FutEnterPrice":futprice, "TrailMul": 1}
            positions.append(position)
        else:
            positionsNotPlaced.append(posc)
    return (positions, positionsNotPlaced)

def StopLossToCost(positions):
    for pos in positions:
        if (pos["Active"]) and pos["PositionConfig"]["SL"] == defs.YES and (pos["SLCond"] - pos["EnterPrice"])*pos["PositionConfig"]["Action"] < 0:
            pos["SLCond"] = pos["EnterPrice"]

def TrailStopLoss(positions, currentcandle):
    for pos in positions:
        if currentcandle.name in pos["OpData"].index:
            optionprice = pos["OpData"].loc[currentcandle.name]['low'] # assuming it is sell side for simplicity
            trailval = pos["EnterPrice"] + pos["TrailMul"]*pos["PositionConfig"]["Action"] * pos["EnterPrice"] * pos["PositionConfig"]["TrailSLPc"] / 100
            if (pos["Active"]) and (pos["PositionConfig"]["SL"] == defs.YES) and (optionprice < trailval):
                pos["SLCond"] = pos["EnterPrice"] + (pos["TrailMul"] - 1)*pos["PositionConfig"]["Action"] * pos["EnterPrice"] * pos["PositionConfig"]["TrailSLPc"] / 100
                pos["TrailMul"] = pos["TrailMul"] + 1

def CheckStopLoss(positions, currentcandle):
    positionstoExit = []
    posconfigtoExit = []
    ExitType = "None"
    for pos in positions:
        if currentcandle.name in pos['OpData'].index :
            if (pos["PositionConfig"]["Action"] == defs.SELL):
                optionprice = pos["OpData"].loc[currentcandle.name]['high'] # 'high' -> 'close
                if (pos["PositionConfig"]["SL"] == defs.YES) and optionprice >= pos['SLCond'] and pos['Active']:
                    positionstoExit.append(pos)
                    posconfigtoExit.append(pos["PositionConfig"])
            elif (pos["PositionConfig"]["Action"] == defs.BUY):
                optionprice = pos["OpData"].loc[currentcandle.name]['low'] # 'low' -> 'close
                optionprice = pd.to_numeric(optionprice)
                if (pos["PositionConfig"]["SL"] == defs.YES) and optionprice <= pos['SLCond'] and pos['Active']:
                    positionstoExit.append(pos)
                    posconfigtoExit.append(pos["PositionConfig"])
    return (positionstoExit, posconfigtoExit)

def CheckStopLossFar(positions, currentcandle):
    positionstoExit = []
    posconfigtoExit = []
    for pos in positions:
        if currentcandle.name in pos['OpData'].index :
            if (pos["PositionConfig"]["Action"] == defs.SELL):
                optionprice = pos["OpData"].loc[currentcandle.name]['high']
                if (pos["PositionConfig"]["SL"] == defs.YES) and optionprice >= pos['SLCondFar'] and pos['Active']:
                    positionstoExit.append(pos)
                    posconfigtoExit.append(pos["PositionConfig"])
            elif (pos["PositionConfig"]["Action"] == defs.BUY):
                optionprice = pos["OpData"].loc[currentcandle.name]['low']
                optionprice = pd.to_numeric(optionprice)
                if (pos["PositionConfig"]["SL"] == defs.YES) and optionprice <= pos['SLCondFar'] and pos['Active']:
                    positionstoExit.append(pos)
                    posconfigtoExit.append(pos["PositionConfig"])
    return (positionstoExit, posconfigtoExit)

def CheckTargetCondition(positions, currentcandle):
    positionstoExit = []
    posconfigtoExit = []
    for pos in positions:
        if currentcandle.name in pos['OpData'].index:
            optionprice = pos["OpData"].loc[currentcandle.name]['high']
            if (pos["PositionConfig"]["Action"] == defs.SELL):
                if (pos["PositionConfig"]["Target"] == defs.YES) and optionprice <= pos['TargetCond'] and pos['Active']:
                    positionstoExit.append(pos)
                    posconfigtoExit.append(pos["PositionConfig"])
            elif (pos["PositionConfig"]["Action"] == defs.BUY):
                if (pos["PositionConfig"]["Target"] == defs.YES) and optionprice >= pos['TargetCond'] and pos['Active']:
                    positionstoExit.append(pos)
                    posconfigtoExit.append(pos["PositionConfig"])
    return (positionstoExit, posconfigtoExit)

def ExitPosition(positionstoExit, currentcandle, ExitReason, OHLC):
    for pos in positionstoExit:
        if (pos["Active"]):
            Str = ""
            if (pos["PositionConfig"]["Action"] == defs.BUY):
                Str = "Buy "
            elif (pos["PositionConfig"]["Action"] == defs.SELL):
                Str = "Sell "
            Str = Str + pos["PositionConfig"]["Type"]
            if (ExitReason == defs.SL):
                exitprice = pos["SLCond"]
                #exitprice = pos["OpData"].loc[currentcandle.name][OHLC]
                exitReason = "SL HIT"
            if (ExitReason == defs.SLPos):
                exitprice = pos["OpData"].loc[currentcandle.name][OHLC]
                exitReason = "SL HIT"
            if (ExitReason == defs.SLFar):
                exitprice = pos["SLCondFar"]
                exitReason = "FAR SL HIT"
            elif (ExitReason == defs.TARGET):
                exitprice = pos["TargetCond"]
                exitReason = "Target Hit"
            elif (ExitReason == defs.SQUAREOFF):
                if currentcandle.name in pos["OpData"].index:
                    # OHLC = close
                    exitprice = pos["OpData"].loc[currentcandle.name][OHLC]
                    exitReason = "Square Off"
                else:
                    idx = pos["OpData"].index[pos["OpData"].index.get_loc(currentcandle.name, method='nearest')]
                    exitprice = pos["OpData"][idx]
            elif (ExitReason == defs.SQUAREOFFEOD):
                if currentcandle.name in pos["OpData"].index:
                    # OHLC = open
                    exitprice = pos["OpData"].loc[currentcandle.name][OHLC]
                    exitReason = "Square Off EOD"
                else:
                    if pos["OpData"].empty:
                        return
                    else:
                        idx = pos["OpData"].index[pos["OpData"].sort_index(axis=0).index.get_loc(currentcandle.name, method='nearest')]
                        exitprice = pos["OpData"].loc[idx][OHLC]
                        exitReason = "Square Off EOD"
            enterprice = pos['EnterPrice']   
            # futenterprice = pos['FutEnterPrice']
            # futexitprice = pos['FutData'].loc[currentcandle.name][OHLC]
            #enterprice = enterprice*(1 + pos["Slippage"]*pos["PositionConfig"]["Action"]/100)
            exitprice = exitprice*(1 - pos["Slippage"]*pos["PositionConfig"]["Action"]/100)
            pos["trades"] = {'EnterPrice': enterprice, 'ExitPrice': exitprice,
                            'EnterTime': pos['Entertime'], 'ExitTime': currentcandle.name.time(),
                            'Reason': exitReason, 'Trade Type': Str, 'EnterSpotPrice': pos["EnterSpotPrice"], "ExitSpotPrice": currentcandle['close'],                            
                            "pnl": (exitprice - enterprice) * pos["PositionConfig"]["Action"] * pos["Qty"],
                            "date": pos["date"], "symbol": pos["OpSymbol"], "Expiry": pos['Expiry']}
            pos["Active"] = False


def GetFinalTrades(positions):
    trades = pd.DataFrame()
    for pos in positions:
        trades = trades.append(pos["trades"], ignore_index=True)
    #trades = trades.append(trades, ignore_index=True)
    return trades













