import atomic as atom
import definitions as defs
import directional as direc
import time

def IntradayTimeReEntry(masterdf, generalconfig, positionconfig):
  spotdata = atom.GetSpotData(masterdf, generalconfig["symbol"])
  placed = False
  positions = []
  trades = []
  MinCounter = 0

  OHLCEnter = 'open'
  exitSLOHLC = 'close'
  exitTGOHLC = 'close'
  exitSQOHLC = 'close'
  exitSQEODOHLC = 'open'

  for s in range(len(spotdata)):
    MinCounter += 1
    currentcandle = spotdata.iloc[s]
    # Check Enter time Condition
    if currentcandle.name.time() == generalconfig["EnterTime"] and not placed:
      (positions, positionsNotPlaced) = atom.EnterPosition(generalconfig, positionconfig, masterdf, positions,
                                                           currentcandle, OHLCEnter)
      placed = True
    if placed:
      # Check time based re-entry. If true, re-enter every "ReEnterEvery" number of minutes.
      if (generalconfig["Timerenter"] == defs.YES):
        if (MinCounter % generalconfig["ReEnterEvery"] == 0):
          (positions, positionsNotPlaced) = atom.EnterPosition(generalconfig, positionconfig, masterdf, positions,
                                                               currentcandle, OHLCEnter)
      # Check Stop Loss Condition
      (postoExitSL, posConfigtoExitSL) = atom.CheckStopLoss(positions, currentcandle)

      # We enter this loop if there is any position where stop-loss is triggered.
      if (len(postoExitSL) > 0):
        atom.ExitPosition(postoExitSL, currentcandle, defs.SL, exitSLOHLC)
        if (generalconfig["SLToCost"] == defs.YES):
          atom.StopLossToCost(positions)
        if (generalconfig["SquareOffSL"] == defs.ALLLEGS):
          atom.ExitPosition(positions, currentcandle, defs.SQUAREOFF, exitSQOHLC)

      # Check Target Profit Condition
      (postoExitTarget, posConfigtoExitTG) = atom.CheckTargetCondition(positions, currentcandle)
      # We enter this loop if there is any position where target profit condition is satisfied.
      if (len(postoExitTarget) > 0):
        ReEnterNextTG = True
        posConfigtoExitTGNext = posConfigtoExitTG
        atom.ExitPosition(postoExitTarget, currentcandle, defs.TARGET, exitTGOHLC)
        if (generalconfig["SquareOffTG"] == defs.ALLLEGS):
          atom.ExitPosition(positions, currentcandle, defs.SQUAREOFF, exitTGOHLC)

      # Square off Remaining Legs EOD
      if (currentcandle.name.time() == generalconfig["ExitTime"]):
        atom.ExitPosition(positions, currentcandle, defs.SQUAREOFFEOD, exitSQEODOHLC)
        trades = atom.GetFinalTrades(positions)
  return trades

def IntraDayStrategy(masterdf, generalconfig, positionconfig):
  spotdata = atom.GetSpotData(masterdf, generalconfig["symbol"])
  placed = False
  positions = []
  trades = []
  MinCounter = 0
  ReEnterCounterSL = 0
  ReEnterCounterTG = 0
  ReEnterNextSL = False
  ReEnterNextTG = False
  CallActive = True
  PutActive = True

  OHLCEnter = 'open'
  exitSLOHLC = 'close'
  exitTGOHLC = 'close'
  exitSQOHLC = 'close'
  exitSQEODOHLC = 'open'

  for s in range(len(spotdata)):
    MinCounter += 1
    currentcandle = spotdata.iloc[s]
    # Check Enter time Condition
    if currentcandle.name.time() == generalconfig["EnterTime"] and not placed:
      (positions, positionsNotPlaced) = atom.EnterPosition(generalconfig, positionconfig, masterdf, positions, currentcandle, OHLCEnter)
      placed = True
      CallActive = True
      PutActive = True
    if placed:
      # Trail Stop Loss Condition
      if (generalconfig["TrailSL"] == defs.YES):
        atom.TrailStopLoss(positions, currentcandle)
      # Check Stop Loss Condition
      (postoExitSL, posConfigtoExitSL) = atom.CheckStopLoss(positions, currentcandle)
      # We enter the loop below if re-entry is true and stop loss was triggered the previous minute.
      if (generalconfig["ReEntrySL"] == defs.YES) and (ReEnterCounterSL < generalconfig["MaxReEnterCounterSL"]) and (ReEnterNextSL) and (MinCounter % generalconfig["REEvery"] == 0):
        ReEnterNextSL = False
        ReEnterCounterSL += 1
        if (generalconfig["SquareOffSL"] == defs.ONELEG):
          (positions, positionsNotPlaced) = atom.EnterPosition(generalconfig, posConfigtoExitSLNext, masterdf, positions,
                                                               currentcandle, OHLCEnter)
        elif (generalconfig["SquareOffSL"] == defs.ALLLEGS):
          (positions, positionsNotPlaced) = atom.EnterPosition(generalconfig, positionconfig, masterdf, positions,
                                                               currentcandle, OHLCEnter)
        elif (generalconfig["SquareOffSL"] == defs.ONELEGSL):
          (positions, positionsNotPlaced) = atom.EnterPosition(generalconfig, positionconfig, masterdf, positions,
                                                               currentcandle, OHLCEnter)
          CallActive = True
          PutActive = True
      # We enter this loop if there is any position where stop-loss is triggered.
      if (len(postoExitSL) > 0):
        if (posConfigtoExitSL[0]["Type"] == defs.CALL):
          CallActive = False
        else:
          PutActive = False
        if(generalconfig["SquareOffSL"] == defs.ONELEGSL):
          if (CallActive == False) and (PutActive == False):
            ReEnterNextSL = True
        else:
          ReEnterNextSL = True
        posConfigtoExitSLNext = posConfigtoExitSL
        atom.ExitPosition(postoExitSL, currentcandle, defs.SL, exitSLOHLC)
        if (generalconfig["SLToCost"] == defs.YES):
          atom.StopLossToCost(positions)
        if (generalconfig["SquareOffSL"] == defs.ALLLEGS):
          atom.ExitPosition(positions, currentcandle, defs.SQUAREOFF, exitSQOHLC)

      # Check Target Profit Condition
      (postoExitTarget, posConfigtoExitTG) = atom.CheckTargetCondition(positions, currentcandle)

      # We enter the loop below if re-entry is true and target profit condition was triggered the previous minute.
      if (generalconfig["ReEntryTG"] == defs.YES) and (ReEnterCounterTG <= generalconfig["MaxReEnterCounterTG"]) and (ReEnterNextTG):
        ReEnterCounterTG += 1
        if (generalconfig["SquareOffTG"] == defs.ONELEG):
          (positions, positionsNotPlaced) = atom.EnterPosition(generalconfig, posConfigtoExitTGNext, masterdf, positions,
                                                               currentcandle, OHLCEnter)
        elif (generalconfig["SquareOffTG"] == defs.ALLLEGS):
          (positions, positionsNotPlaced) = atom.EnterPosition(generalconfig, positionconfig, masterdf, positions,
                                                               currentcandle, OHLCEnter)

      # We enter this loop if there is any position where target profit condition is satisfied.
      if (len(postoExitTarget) > 0):
        ReEnterNextTG = True
        posConfigtoExitTGNext = posConfigtoExitTG
        atom.ExitPosition(postoExitTarget, currentcandle, defs.TARGET, exitTGOHLC)
        if (generalconfig["SquareOffTG"] == defs.ALLLEGS):
          atom.ExitPosition(positions, currentcandle, defs.SQUAREOFF, exitTGOHLC)

      # Square off Remaining Legs EOD
      if (currentcandle.name.time() == generalconfig["ExitTime"]):
        atom.ExitPosition(positions, currentcandle, defs.SQUAREOFFEOD, exitSQEODOHLC)
        trades = atom.GetFinalTrades(positions)
  return trades

def OverNightDirectional(masterdf, positions, generalconfig, positionconfig):
  spotdata = atom.GetSpotData(masterdf,generalconfig["symbol"])
  trades = []
  OHLCEnter = 'open'
  exitSQEODOHLC = 'open'
  direc.UpdatePosition(masterdf, positions)
  for s in range(len(spotdata)):
    currentcandle = spotdata.iloc[s]
    if (currentcandle.name.time() == generalconfig["StartCheckTime"]):
      startVal = currentcandle["open"]
    if (currentcandle.name.time() == generalconfig["EndCheckTime"]):
      endVal = currentcandle["open"]
    if currentcandle.name.time() == generalconfig["EnterTime"] and currentcandle.name.weekday() in generalconfig['EnterDay']:
      if (startVal < endVal):
        if (generalconfig["SType"] == "Trend"):
          outlook = defs.BULL
        else:
          outlook = defs.BEAR
      else:
        if (generalconfig["SType"] == "Trend"):
          outlook = defs.BEAR
        else:
          outlook = defs.BULL
      if (outlook == defs.BULL):
        (positions, positionsNotPlaced) = direc.EnterPosition(generalconfig, positionconfig, masterdf, positions,
                                                            currentcandle, OHLCEnter, defs.BULL)
      else:
        (positions, positionsNotPlaced) = direc.EnterPosition(generalconfig, positionconfig, masterdf, positions,
                                                            currentcandle, OHLCEnter, defs.BEAR)

    # Square off Legs at ExitTime
    if (currentcandle.name.time() == generalconfig['ExitTime']) and (currentcandle.name.weekday() in generalconfig["ExitDay"]):
      direc.ExitPosition(positions, currentcandle, defs.SQUAREOFFEOD, exitSQEODOHLC)
      trades = atom.GetFinalTrades(positions)
      positions = []
  return (trades, positions)

def MultiDayStrategy(masterdf, positions, generalconfig, positionconfig):
  spotdata = atom.GetSpotData(masterdf,generalconfig["symbol"])
  trades = []
  MinCounter = 0
  OHLCEnter = 'open'
  exitSLOHLC = 'close'
  exitTGOHLC = 'close'
  exitSQEODOHLC = 'open'

  # Check if there is any position where there is a "SL" or "Target" Condition. If not, there is no need to
  # loop and check stop loss/target conditions.
  loop = False
  for posc in positionconfig:
    if (posc["SL"] == defs.YES) or (posc["Target"] == defs.YES):
      loop = True

  # Update the opdata in the positions for the active positions still open!
  atom.UpdatePosition(masterdf, positions)
  for s in range(len(spotdata)):
    MinCounter += 1
    currentcandle = spotdata.iloc[s]
    # Check Enter time and Enter Day Condition
    if currentcandle.name.time() == generalconfig["EnterTime"] and currentcandle.name.weekday() in generalconfig['EnterDay']:
      (positions, positionsNotPlaced) = atom.EnterPosition(generalconfig, positionconfig, masterdf, positions, currentcandle, OHLCEnter)

    if loop:
      # Check Stop Loss Condition
      (postoExitSL, posConfigtoExitSL) = atom.CheckStopLoss(positions, currentcandle)

      # We enter this loop if there is any position where stop-loss is triggered.
      if (len(postoExitSL) > 0):
        atom.ExitPosition(postoExitSL, currentcandle, defs.SLPos, exitSLOHLC)

      # Check Target Profit Condition
      (postoExitTarget, posConfigtoExitTG) = atom.CheckTargetCondition(positions, currentcandle)

      # We enter this loop if there is any position where target profit condition is satisfied.
      if (len(postoExitTarget) > 0):
        ReEnterNextTG = True
        posConfigtoExitTGNext = posConfigtoExitTG
        atom.ExitPosition(postoExitTarget, currentcandle, defs.TARGET, exitTGOHLC)

    # Square off Remaining Legs EOD
    if (currentcandle.name.time() == generalconfig['ExitTime']) and (currentcandle.name.weekday() in generalconfig["ExitDay"]):
      atom.ExitPosition(positions, currentcandle, defs.SQUAREOFFEOD, exitSQEODOHLC)
      trades = atom.GetFinalTrades(positions)
      positions = []
  return (trades, positions)


def DirectionalStrategy(data, masterdf, generalconfig, positionconfig, TIconfig, start_date):
  spotdata = data[data.index.date == start_date]
  spotdatafull = atom.GetSpotData(masterdf, generalconfig["symbol"])
  placedBull = False
  placedBear = False
  exitDone = False # if exit (EOD) is done, we do not go to the exit condition again.
  positions = []
  trades = []
  BullReEnterCounter = 0
  BearReEnterCounter = 0
  OHLCEnter = 'open'
  exitSLOHLC = 'close'
  exitTGOHLC = 'close'
  exitSQEODOHLC = 'close'
  for s in range(len(spotdata)): # 
    currentcandle = spotdata.iloc[s]
    if (currentcandle.name in spotdatafull.index):
      sfull = spotdatafull.index.get_loc(currentcandle.name)
      if (sfull < len(spotdatafull)-1):
        nextcandle = spotdatafull.iloc[sfull+1]
      else:
        nextcandle = currentcandle
    else:
      nextcandle = currentcandle
    (bullentry, bearentry) = direc.CheckEntryCondition(currentcandle, TIconfig)
    # Check Enter Condition
    if bullentry and not placedBull and (BullReEnterCounter < generalconfig["MaxBullReEnterCounter"]):
      (positions, positionsNotPlaced) = direc.EnterPosition(generalconfig, positionconfig, masterdf, positions, nextcandle, OHLCEnter, defs.BULL)
      data.loc[currentcandle.name]['EntrySignal'] = defs.ENTERBULLPOSITION
      placedBull = True
      BullReEnterCounter += 1
    if bearentry and not placedBear and (BearReEnterCounter < generalconfig["MaxBearReEnterCounter"]):
      (positions, positionsNotPlaced) = direc.EnterPosition(generalconfig, positionconfig, masterdf, positions, nextcandle, OHLCEnter, defs.BEAR)
      data.loc[currentcandle.name]['EntrySignal'] = defs.ENTERBEARPOSITION
      placedBear = True
      BearReEnterCounter += 1
    
    if placedBull or placedBear:
      if (generalconfig["TrailSL"] == defs.YES):
        atom.TrailStopLoss(positions, currentcandle)
      # Check Stop Loss Condition
      if (generalconfig["StopLoss"]) and (currentcandle.name.time() <= generalconfig["ExitTime"]):
        if (generalconfig["StopLossCond"] == "TIBased") or (generalconfig["StopLossCond"] == "TIPremiumBased"):
          postoExitSL = direc.CheckStopLossTI(positions, currentcandle, nextcandle, TIconfig)
          if (len(postoExitSL) > 0):
            direc.ExitPosition(postoExitSL, nextcandle, defs.SL, exitSLOHLC)
            data.loc[currentcandle.name]['ExitSignal'] = defs.STOPLOSSHIT
            if (generalconfig["Reenter"] == defs.YES):
              for pos in postoExitSL:
                if pos["stance"] == defs.BULL:
                  placedBull = False
                elif pos["stance"] == defs.BEAR:
                  placedBear = False
        if (generalconfig["StopLossCond"] == "PremiumBased") or (generalconfig["StopLossCond"] == "TIPremiumBased"):
          if (generalconfig["SLTGContinuous"] == defs.YES):
            sbegin = sfull + 1
            nextcandles = spotdata.iloc[s+1]
            if nextcandles.name in spotdatafull.index:
              send = spotdatafull.index.get_loc(nextcandles.name)
              # We loop through every minute in full spotdata so we can check the stop loss continuously
              for smin in range(sbegin, send+1):
                mincandle = spotdatafull.iloc[smin]
                (postoExitSL, posConfigtoExitSL) = atom.CheckStopLoss(positions, mincandle)
            # We enter this loop if there is any position where stop-loss is triggered.
                if (len(postoExitSL) > 0):
                  direc.ExitPositionPremium(postoExitSL, mincandle, defs.SL, exitSLOHLC)
                  data.loc[currentcandle.name]['ExitSignal'] = defs.STOPLOSSHIT
                  if (generalconfig["Reenter"] == defs.YES):
                    for pos in postoExitSL:
                      if pos["stance"] == defs.BULL:
                        placedBull = False
                      elif pos["stance"] == defs.BEAR:
                        placedBear = False
          else:
            (postoExitSL, posConfigtoExitSL) = atom.CheckStopLoss(positions, nextcandle)
            if (len(postoExitSL) > 0):
              direc.ExitPositionPremium(postoExitSL, nextcandle, defs.SL, exitSLOHLC)
              data.loc[currentcandle.name]['ExitSignal'] = defs.STOPLOSSHIT
              if (generalconfig["Reenter"] == defs.YES):
                for pos in postoExitSL:
                  if pos["stance"] == defs.BULL:
                    placedBull = False
                  elif pos["stance"] == defs.BEAR:
                    placedBear = False

      # Check Target Profit Condition
      if (generalconfig["Target"]) and (currentcandle.name.time() <= generalconfig["ExitTime"]):
        if (generalconfig["TargetCond"] == "TIBased") or (generalconfig["TargetCond"] == "TIPremiumBased"):
          postoExitTarget = direc.CheckTargetConditionTI(positions, currentcandle, nextcandle, TIconfig)
          if (len(postoExitTarget) > 0):
            direc.ExitPosition(postoExitTarget, nextcandle, defs.SL, exitTGOHLC)
            data.loc[currentcandle.name]['ExitSignal'] = defs.TARGETREACHED
            if (generalconfig["Reenter"] == defs.YES):
              for pos in postoExitTarget:
                if pos["stance"] == defs.BULL:
                  placedBull = False
                elif pos["stance"] == defs.BEAR:
                  placedBear = False
        if (generalconfig["TargetCond"] == "PremiumBased") or (generalconfig["TargetCond"] == "TIPremiumBased"):
          # We loop through every minute in full spotdata so we can check the target condition continuously
          if (generalconfig["SLTGContinuous"] == defs.YES):
            sbegin = sfull + 1
            nextcandles = spotdata.iloc[s + 1]
            if nextcandles.name in spotdatafull.index:
              send = spotdatafull.index.get_loc(nextcandles.name)
              for smin in range(sbegin, send+1):
                mincandle = spotdatafull.iloc[smin]
                (postoExitTarget, posConfigtoExitTG) = atom.CheckTargetCondition(positions, mincandle)
                # We enter this loop if there is any position where target profit condition is satisfied.
                if (len(postoExitTarget) > 0):
                  direc.ExitPosition(postoExitTarget, mincandle, defs.TARGET, exitTGOHLC)
                  data.loc[currentcandle.name]['ExitSignal'] = defs.TARGETREACHED
                  if (generalconfig["Reenter"] == defs.YES):
                    for pos in postoExitTarget:
                      if pos["stance"] == defs.BULL:
                        placedBull = False
                      elif pos["stance"] == defs.BEAR:
                        placedBear = False
          else:
            (postoExitTarget, posConfigtoExitTG) = atom.CheckTargetCondition(positions, nextcandle)
            if (len(postoExitTarget) > 0):
              direc.ExitPosition(postoExitTarget, nextcandle, defs.TARGET, exitTGOHLC)
              data.loc[currentcandle.name]['ExitSignal'] = defs.TARGETREACHED
              if (generalconfig["Reenter"] == defs.YES):
                for pos in postoExitTarget:
                  if pos["stance"] == defs.BULL:
                    placedBull = False
                  elif pos["stance"] == defs.BEAR:
                    placedBear = False

    # Square off Remaining Legs EOD
      if (currentcandle.name.time() >= generalconfig["ExitTime"]) and not exitDone:
        if direc.CheckActivePositions(positions) == True:
          data.loc[currentcandle.name]['ExitSignal'] = defs.EXITTIME
        direc.ExitPosition(positions, currentcandle, defs.SQUAREOFFEOD, exitSQEODOHLC)
        # trades = atom.GetFinalTrades(positions)
        exitDone = True
      trades = atom.GetFinalTrades(positions)
  return trades

def OpeningRangeBreakout(masterdf, generalconfig, positionconfig):
  spotdata = atom.GetSpotData(masterdf,generalconfig["symbol"])
  placedBull = False
  placedBear = False
  initialized = False
  positions = []
  trades = []
  MinCounter = 0

  OHLCEnter = 'open'
  OHLCUntil = 'open'
  OHLCBreakout = 'open'
  exitSLOHLC = 'close'
  exitTGOHLC = 'close'
  exitSQEODOHLC = 'open'
  highestCEPrice = 0
  highestPEPrice = 0
  lowestCEPrice = 1000000
  lowestPEPrice = 1000000
  for s in range(len(spotdata)):
    MinCounter += 1
    currentcandle = spotdata.iloc[s]
    # Get Strike Prices for Closest Premium at the start
    if currentcandle.name.time() == generalconfig["EnterTime"]:
      (beststrikeCE, minval) = direc.FindStrike(masterdf, generalconfig["Premium"], currentcandle.name, generalconfig["StartStrike"], 
                                                generalconfig["EndStrikeStrike"], defs.CALL, OHLCEnter, generalconfig["symbol"])
      (beststrikePE, minval) = direc.FindStrike(masterdf, generalconfig["Premium"], currentcandle.name, generalconfig["StartStrike"], 
                                                generalconfig["EndStrikeStrike"], defs.PUT, OHLCEnter, generalconfig["symbol"])
      exp = atom.GetExpiry(masterdf, generalconfig["symbol"])
      opdfCE = masterdf[masterdf['symbol'] == generalconfig["symbol"] + exp + str(beststrikeCE) + defs.CALL]
      opdfPE = masterdf[masterdf['symbol'] == generalconfig["symbol"] + exp + str(beststrikePE) + defs.PUT]
      initialized = True
    # Observe the highest premium in the second part
    if initialized and (currentcandle.name.time() >= generalconfig["EnterTime"]) and (currentcandle.name.time() <= generalconfig["Until"]):
      if (generalconfig["Type"] == defs.BUY):
        if (currentcandle.name in opdfCE.index) and (highestCEPrice < opdfCE.loc[currentcandle.name][OHLCUntil]):
          highestCEPrice = opdfCE.loc[currentcandle.name][OHLCUntil]
        if (currentcandle.name in opdfPE.index) and (highestPEPrice < opdfPE.loc[currentcandle.name][OHLCUntil]):
          highestPEPrice = opdfPE.loc[currentcandle.name][OHLCUntil]
      elif (generalconfig["Type"] == defs.SELL):
        if (currentcandle.name in opdfCE.index) and (lowestCEPrice > opdfCE.loc[currentcandle.name][OHLCUntil]):
          lowestCEPrice = opdfCE.loc[currentcandle.name][OHLCUntil]
        if (currentcandle.name in opdfPE.index) and (lowestPEPrice > opdfPE.loc[currentcandle.name][OHLCUntil]):
          lowestPEPrice = opdfPE.loc[currentcandle.name][OHLCUntil]
    # Look for break out signal
    if (currentcandle.name.time() == generalconfig["Until"]):
        breakoutCEPriceHigh = highestCEPrice*(1 + generalconfig["BreakoutFactor"]/100)
        breakoutPEPriceHigh = highestPEPrice*(1 + generalconfig["BreakoutFactor"]/100)
        breakoutCEPriceLow = lowestCEPrice * (1 - generalconfig["BreakoutFactor"] / 100)
        breakoutPEPriceLow = lowestPEPrice * (1 - generalconfig["BreakoutFactor"] / 100)
    if initialized and currentcandle.name.time() >= generalconfig["Until"]:
      if (generalconfig["OpType"] == defs.BUY):
        if (generalconfig["Type"] == defs.TREND):
          if (currentcandle.name in opdfCE.index) and opdfCE.loc[currentcandle.name][OHLCBreakout] >= breakoutCEPriceHigh and not placedBull:
            (positions, positionsNotPlaced) = direc.EnterPositionStrike(generalconfig, positionconfig, masterdf, positions, currentcandle, OHLCBreakout, defs.BULL, beststrikeCE)
            placedBull = True
          if (currentcandle.name in opdfPE.index) and opdfPE.loc[currentcandle.name][OHLCBreakout] >= breakoutPEPriceHigh and not placedBear:
            (positions, positionsNotPlaced) = direc.EnterPositionStrike(generalconfig, positionconfig, masterdf, positions, currentcandle, OHLCBreakout, defs.BEAR, beststrikePE)
            placedBear = True
        elif (generalconfig["Type"] == defs.MR):
          if (currentcandle.name in opdfCE.index) and opdfCE.loc[currentcandle.name][OHLCBreakout] <= breakoutCEPriceLow and not placedBear:
            (positions, positionsNotPlaced) = direc.EnterPositionStrike(generalconfig, positionconfig, masterdf, positions, currentcandle, OHLCBreakout, defs.BEAR, beststrikeCE)
            placedBear = True
          if (currentcandle.name in opdfPE.index) and opdfPE.loc[currentcandle.name][OHLCBreakout] <= breakoutPEPriceLow and not placedBull:
            (positions, positionsNotPlaced) = direc.EnterPositionStrike(generalconfig, positionconfig, masterdf, positions, currentcandle, OHLCBreakout, defs.BULL, beststrikePE)
            placedBull = True
      elif (generalconfig["OpType"] == defs.SELL):
        if (currentcandle.name in opdfCE.index) and opdfCE.loc[currentcandle.name][OHLCBreakout] <= breakoutCEPrice and not placedBear:
          (positions, positionsNotPlaced) = direc.EnterPositionStrike(generalconfig, positionconfig, masterdf, positions, currentcandle, OHLCBreakout, defs.BEAR, beststrikeCE)
          placedBear = True
        if (currentcandle.name in opdfPE.index) and opdfPE.loc[currentcandle.name][OHLCBreakout] <= breakoutPEPrice and not placedBull:
          (positions, positionsNotPlaced) = direc.EnterPositionStrike(generalconfig, positionconfig, masterdf, positions, currentcandle, OHLCBreakout, defs.BULL, beststrikePE)
          placedBull = True
    if placedBull or placedBear:
      (postoExitSL, posConfigtoExitSL) = atom.CheckStopLoss(positions, currentcandle)
      # We enter this loop if there is any position where stop-loss is triggered.
      if (len(postoExitSL) > 0):
        direc.ExitPosition(postoExitSL, currentcandle, defs.SL, exitSLOHLC)
        
      # Check Target Profit Condition
      (postoExitTarget, posConfigtoExitTG) = atom.CheckTargetCondition(positions, currentcandle)
      # We enter this loop if there is any position where target profit condition is satisfied.
      if (len(postoExitTarget) > 0):
        direc.ExitPosition(postoExitTarget, currentcandle, defs.TARGET, exitTGOHLC)

      # Square off Remaining Legs EOD
      if (currentcandle.name.time() == generalconfig["ExitTime"]):
        direc.ExitPosition(positions, currentcandle, defs.SQUAREOFFEOD, exitSQEODOHLC)
        trades = atom.GetFinalTrades(positions)  

  return trades






