import definitions as defs

# INTRADAY STRANGLE SEARCH BANKNIFTY
ind_strangle_BN_1 = {"SquareOffSL":defs.ONELEG, "SquareOffTG": defs.ONELEG, "symbol": defs.BN, "ReEntrySL": defs.YES, "ReEntryTG": defs.YES, "SLEvery":13, "SLPcFar":100,
            "MaxReEnterCounterSL": 2, "MaxReEnterCounterTG": 7, "SLtoCost":defs.NO, "SL":defs.YES, "Target":defs.YES, "SLPc":25, "TargetPc":70, "Delta":1100}

ind_strangle_BN_2 = {"SquareOffSL":defs.ONELEG, "SquareOffTG": defs.ONELEG, "symbol": defs.BN, "ReEntrySL": defs.YES, "ReEntryTG": defs.YES, "SLEvery":14, "SLPcFar":100,
            "MaxReEnterCounterSL": 7, "MaxReEnterCounterTG": 7, "SLtoCost":defs.NO, "SL":defs.YES, "Target":defs.NO, "SLPc":15, "TargetPc":70, "Delta":1200}

ind_strangle_BN_3 = {"SquareOffSL":defs.ONELEG, "SquareOffTG": defs.ONELEG, "symbol": defs.BN, "ReEntrySL": defs.YES, "ReEntryTG": defs.YES, "SLEvery":14, "SLPcFar":100,
            "MaxReEnterCounterSL": 1, "MaxReEnterCounterTG": 8, "SLtoCost":defs.NO, "SL":defs.YES, "Target":defs.YES, "SLPc":25, "TargetPc":70, "Delta":1100}

# INTRADAY STRANGLE SEARCH NIFTY
ind_strangle_N_1 = {"SquareOffSL":defs.ONELEG, "SquareOffTG": defs.ONELEG, "symbol": defs.N, "ReEntrySL": defs.YES, "ReEntryTG": defs.YES, "SLEvery":13, "SLPcFar":100,
            "MaxReEnterCounterSL": 2, "MaxReEnterCounterTG": 7, "SLtoCost":defs.NO, "SL":defs.YES, "Target":defs.YES, "SLPc":25, "TargetPc":70, "Delta":1100}

ind_strangle_N_2 = {"SquareOffSL":defs.ONELEG, "SquareOffTG": defs.ONELEG, "symbol": defs.N, "ReEntrySL": defs.YES, "ReEntryTG": defs.YES, "SLEvery":14, "SLPcFar":100,
            "MaxReEnterCounterSL": 7, "MaxReEnterCounterTG": 7, "SLtoCost":defs.NO, "SL":defs.YES, "Target":defs.NO, "SLPc":15, "TargetPc":70, "Delta":1200}

ind_strangle_N_3 = {"SquareOffSL":defs.ONELEG, "SquareOffTG": defs.ONELEG, "symbol": defs.N, "ReEntrySL": defs.YES, "ReEntryTG": defs.YES, "SLEvery":14, "SLPcFar":100,
            "MaxReEnterCounterSL": 1, "MaxReEnterCounterTG": 8, "SLtoCost":defs.NO, "SL":defs.YES, "Target":defs.YES, "SLPc":25, "TargetPc":70, "Delta":1100}

# INTRADAY STRADDLE SEARCH BANKNIFTY
ind_straddle_BN_1 = {"SquareOffSL":defs.ALLLEGS, "SquareOffTG": defs.ONELEG, "symbol": defs.BN, "ReEntrySL": defs.YES, "ReEntryTG": defs.YES, "SLEvery":15, "SLPcFar":100,
                "MaxReEnterCounterSL": 1, "MaxReEnterCounterTG": 3, "SLtoCost":defs.YES, "SL":defs.YES, "Target":defs.NO, "SLPc":30, "TargetPc":50}

ind_straddle_BN_2 = {"SquareOffSL":defs.ONELEG, "SquareOffTG": defs.ALLLEGS, "symbol": defs.BN, "ReEntrySL": defs.YES, "ReEntryTG": defs.NO, "SLEvery":5, "SLPcFar":100,
                "MaxReEnterCounterSL": 10, "MaxReEnterCounterTG": 1, "SLtoCost":defs.YES, "SL":defs.YES, "Target":defs.NO, "SLPc":30, "TargetPc":50}

ind_straddle_BN_3 = {"SquareOffSL": defs.ALLLEGS, "SquareOffTG": defs.ONELEG, "symbol": defs.BN, "ReEntrySL": defs.YES, "ReEntryTG": defs.YES, "SLEvery":20, "SLPcFar":500,
                "MaxReEnterCounterSL": 6, "MaxReEnterCounterTG": 2, "SLtoCost":defs.NO, "SL":defs.YES, "Target":defs.NO, "SLPc":30, "TargetPc":70}

ind_straddle_BN_4 = {"SquareOffSL": defs.ONELEGSL, "SquareOffTG": defs.ONELEG, "symbol": defs.BN, "ReEntrySL": defs.YES, "ReEntryTG": defs.YES, "SLEvery":20, "SLPcFar":500,
                "MaxReEnterCounterSL": 6, "MaxReEnterCounterTG": 2, "SLtoCost":defs.NO, "SL":defs.YES, "Target":defs.NO, "SLPc":30, "TargetPc":70}

# INTRADAY STRADDLE SEARCH NIFTY
ind_straddle_N_1 = {"SquareOffSL":defs.ALLLEGS, "SquareOffTG": defs.ONELEG, "symbol": defs.N, "ReEntrySL": defs.YES, "ReEntryTG": defs.YES, "SLEvery":15, "SLPcFar":100,
                "MaxReEnterCounterSL": 1, "MaxReEnterCounterTG": 3, "SLtoCost":defs.YES, "SL":defs.YES, "Target":defs.NO, "SLPc":30, "TargetPc":50}

ind_straddle_N_2 = {"SquareOffSL":defs.ONELEG, "SquareOffTG": defs.ALLLEGS, "symbol": defs.N, "ReEntrySL": defs.YES, "ReEntryTG": defs.NO, "SLEvery":20, "SLPcFar":100,
                "MaxReEnterCounterSL": 10, "MaxReEnterCounterTG": 1, "SLtoCost":defs.YES, "SL":defs.YES, "Target":defs.NO, "SLPc":30, "TargetPc":50}

ind_straddle_N_3 = {"SquareOffSL": 2, "SquareOffTG": 1, "symbol": defs.N, "ReEntrySL": 1, "ReEntryTG": 1, "SLEvery":20, "SLPcFar":100,
                "MaxReEnterCounterSL": 6, "MaxReEnterCounterTG": 2, "SLtoCost":0, "SL":1, "Target":0, "SLPc":30, "TargetPc":70}

rsi2Nb1 = {'Delta': 1200, 'Resample': 4, 'SLPc': 15, 'TBear1': 65, 'TBear2': 85, 'TBull1': 20, 'TBull2': 10, 'TargetPc': 80, 'SL': defs.NO, 'Target': defs.NO,
            'reenter': 0, 'rolling': 1, 'window1': 18, 'window2': 4, 'action': defs.BUY, 'symbol': defs.N, 'SLTGContinuous': defs.YES}