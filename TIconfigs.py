import operator
import definitions as defs

TIconfigRSI_ADX = [{"TI": "RSI", "columnname": "RSI14", "ThreshBull": 60, "ThreshBear": 40, "Window": 14, "SL": defs.YES, "Target": defs.YES, "SLBull": 40, "SLBear": 60, 
           "TargetBull": 77, "TargetBear": 18, "BullOperator": operator.gt, "BearOperator": operator.lt,
                    "SLBullOperator": operator.lt, "SLBearOperator": operator.gt,"TBullOperator": operator.gt, "TBearOperator": operator.lt},
			{"TI": "ADX","columnname":"ADX14", "Window": 14, "ThreshBull": 20, "ThreshBear": 20, "SL": defs.NO, "Target": defs.NO, 
           "BullOperator": operator.gt, "BearOperator": operator.gt}]

TIconfig2_RSI = [{"TI": "RSI", "columnname": "RSI14", "ThreshBull": 40, "ThreshBear": 60, "Window": 14, "SL": defs.NO, "Target": defs.NO,  
            "BullOperator": operator.lt, "BearOperator": operator.gt}, 
			{"TI": "RSI","columnname":"RSI2", "Window": 2, "ThreshBull": 10, "ThreshBear": 90, "SL": defs.NO, "Target": defs.NO, 
            "BullOperator": operator.gt, "BearOperator": operator.gt}]

TIconfigBB1 = [{"TI": "BB", "columnname":"bbsignal", "ThreshBull": 0, "ThreshBear": 1, "period": 20,"stddev":2, "SL": defs.YES, "Target": defs.YES,
                "SLBull": -0.3, "SLBear": 1.3, "TargetBull": 0.7, "TargetBear": 0.3, "BullOperator": operator.lt, "BearOperator": operator.gt,
               "SLBullOperator": operator.lt, "SLBearOperator": operator.gt, "TBullOperator": operator.gt, "TBearOperator": operator.lt}]

TIconfigBB2 = [{"TI": "BB", "columnname":"bbsignal", "ThreshBull": 1, "ThreshBear": 0, "period": 20,"stddev":2, "SL": defs.YES, "Target": defs.YES,
                "SLBull": 0.7, "SLBear": 0.3, "TargetBull": 2, "TargetBear": -1, "BullOperator": operator.gt, "BearOperator": operator.lt,
               "SLBullOperator": operator.lt, "SLBearOperator": operator.gt, "TBullOperator": operator.gt, "TBearOperator": operator.lt}]

TIconfigST = [{"TI": "ST", "columnname":"ST", "ThreshBull": 0, "ThreshBear": 0, "period": 10,"multiplier":2, "SL": defs.NO, "Target": defs.NO,
                "BullOperator": operator.gt, "BearOperator": operator.lt}]