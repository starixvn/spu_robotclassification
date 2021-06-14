CREATE TABLE `TrainResults` (
  `CustID` bigint unsigned NOT NULL,
  `CategoryID` tinyint unsigned NOT NULL,
  `HyperParamsID` smallint unsigned NOT NULL,
  `Mode` decimal(10,4) NOT NULL,
  `SuspiciousWinDay` decimal(15,4) NOT NULL,
  `SuspiciousLoseDay` decimal(15,4) NOT NULL,
  `Streak` smallint NOT NULL,
  `ActiveDay` int unsigned NOT NULL,
  `OutstandingBC` decimal(6,4) DEFAULT NULL,
  `OutstandingTO` decimal(6,4) DEFAULT NULL,
  `InternalBC` decimal(6,4) DEFAULT NULL,
  `InternalTO` decimal(6,4) DEFAULT NULL,
  `LastScannedDate` date NOT NULL,
  PRIMARY KEY (`CustID`,`CategoryID`,`HyperParamsID`),
  KEY `LastScannedDate` (`LastScannedDate`),
  KEY `IX_TrainResults_HyperParamsID` (`HyperParamsID` DESC)
) ENGINE=InnoDB;


CREATE TABLE `WinlossPrediction` (
  `CustID` bigint unsigned NOT NULL,
  `CategoryID` tinyint unsigned NOT NULL,
  `PredictDate` datetime NOT NULL,
  `HyperParamsID` smallint unsigned NOT NULL,
  `Mode` decimal(10,4) NOT NULL,
  `SuspiciousWinDay` decimal(15,4) NOT NULL,
  `SuspiciousLoseDay` decimal(10,4) NOT NULL,
  `IsPrediction` bit(1) DEFAULT b'0',
  `IsPredictWin` bit(1) DEFAULT NULL,
  `IsTruthWin` bit(1) DEFAULT NULL,
  PRIMARY KEY (`CustID`,`CategoryID`,`PredictDate`,`HyperParamsID`),
  KEY `IX_WinlossPrediction_HyperParamsID` (`HyperParamsID` DESC)
) ENGINE=InnoDB;