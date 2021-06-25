DROP PROCEDURE IF EXISTS `SPU_AIML_InsertWinlossPrediction`;

DELIMITER $$
CREATE DEFINER=`AIMLOwner`@`%` PROCEDURE `SPU_AIML_InsertWinlossPrediction`(
	IN 	ip_PredictionData 	JSON,
	IN 	ip_ScanDate			DATETIME,
    
    OUT op_ErrorMessage 	VARCHAR(200)
)
    SQL SECURITY INVOKER
BEGIN
	/*
		Created:	20210422@Long.Luu
		Task:		Insert Train Results [Redmine ID: #0000]
		DB:			SPU_AIML
		Original: 

		Revisions:
			- 20210422@Long.Luu: Created [Redmine ID: #0000]
            
		Example:
			call SPU_AIML.SPU_AIML_InsertWinlossPrediction ('[{"C": 43600693, "CAT": 1, "M": 5.1, "SWD": 5, "SLD": 2, "IP": 1, "IPW": 1, "IPTW": 1, "PID":1}]','2021-04-22',@msg);    
	*/ 

    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN         
        GET DIAGNOSTICS CONDITION 1 op_ErrorMessage = MESSAGE_TEXT;
    END;
    
    DROP TEMPORARY TABLE IF EXISTS Temp_PredictionStats;    
	CREATE TEMPORARY TABLE Temp_PredictionStats 
    (	 
			CustID						BIGINT UNSIGNED	NOT NULL
		, 	CategoryID					TINYINT UNSIGNED NOT NULL
        ,	HyperParamsID				SMALLINT UNSIGNED
        ,	PredictDate					DATETIME
		, 	Counter						SMALLINT UNSIGNED
        , 	PRIMARY KEY	    PK_Temp_PredictionStats(CustID,CategoryID,HyperParamsID) 
    );      
    
    DROP TEMPORARY TABLE IF EXISTS Temp_PredictionStats_Cloned;    
	CREATE TEMPORARY TABLE Temp_PredictionStats_Cloned 
    (	 
			CustID						BIGINT UNSIGNED	NOT NULL
		, 	CategoryID					TINYINT UNSIGNED NOT NULL
        ,	HyperParamsID				SMALLINT UNSIGNED
        , 	PRIMARY KEY	    PK_Temp_PredictionStats_Cloned(CustID,CategoryID,HyperParamsID) 
    );      
    
    DROP TEMPORARY TABLE IF EXISTS Temp_PredictionData;    
	CREATE TEMPORARY TABLE Temp_PredictionData 
    (	 
			CustID						BIGINT UNSIGNED	NOT NULL
		, 	CategoryID					TINYINT UNSIGNED NOT NULL
		, 	`Mode`						DECIMAL(10,4) NOT NULL
		, 	SuspiciousWinDay			DECIMAL(15,4) NOT NULL
		, 	SuspiciousLoseDay			DECIMAL(10,4) NOT NULL
        , 	IsPrediction				SMALLINT UNSIGNED NOT NULL
        ,	IsPredictWin				BIT DEFAULT 1
        ,	IsPreviousTruthWin			BIT DEFAULT 1
        ,	HyperParamsID				SMALLINT UNSIGNED
        , 	PRIMARY KEY	    PK_Temp_PredictionData(CustID,CategoryID) 
    );      
    
    INSERT INTO Temp_PredictionData(CustID, CategoryID, `Mode`, SuspiciousWinDay, SuspiciousLoseDay, IsPrediction, IsPredictWin, IsPreviousTruthWin, HyperParamsID)
	SELECT 	tmpTable.CustID
		, 	tmpTable.CategoryID
		, 	tmpTable.`Mode`
        , 	tmpTable.SuspiciousWinDay
        , 	tmpTable.SuspiciousLoseDay
        , 	tmpTable.IsPrediction
        , 	tmpTable.IsPredictWin
        , 	tmpTable.IsPreviousTruthWin
        ,	tmpTable.HyperParamsID
	FROM JSON_TABLE(ip_PredictionData,
		 "$[*]" COLUMNS(
			  CustID 				BIGINT UNSIGNED		PATH "$.C"
			, CategoryID			TINYINT UNSIGNED	PATH "$.CAT"
			, `Mode`				DECIMAL(10,4)		PATH "$.M"
            , SuspiciousWinDay		DECIMAL(15,4) 		PATH "$.SWD"
            , SuspiciousLoseDay		DECIMAL(10,4)		PATH "$.SLD"
            , IsPrediction			BIT					PATH "$.IP"
            , IsPredictWin			BIT					PATH "$.IPW"
            , IsPreviousTruthWin	BIT					PATH "$.IPTW"
            , HyperParamsID			SMALLINT UNSIGNED 	PATH "$.PID"
		 )) AS tmpTable;  
	
    INSERT INTO Temp_PredictionStats(CustID, CategoryID, HyperParamsID, PredictDate)
    SELECT a.CustID, a.CategoryID, MAX(a.HyperParamsID), MAX(a.PredictDate)
    FROM SPU_AIML.WinlossPrediction AS a
		INNER JOIN Temp_PredictionData AS t ON t.CustID = a.CustID AND t.CategoryID = a.CategoryID
	GROUP BY a.CustID, a.CategoryID;
    
    INSERT INTO Temp_PredictionStats_Cloned(CustID, CategoryID, HyperParamsID)
    SELECT a.CustID, a.CategoryID, a.HyperParamsID
    FROM Temp_PredictionStats AS a;
    
    SET SQL_SAFE_UPDATES = 0;
    UPDATE Temp_PredictionStats AS t
		INNER JOIN (SELECT a.CustID, a.CategoryID, a.HyperParamsID, COUNT(1) AS Counter
					FROM Temp_PredictionStats_Cloned AS t1
						INNER JOIN SPU_AIML.WinlossPrediction AS a 
							ON t1.CustID = a.CustID AND t1.CategoryID = a.CategoryID AND t1.HyperParamsID = a.HyperParamsID
					GROUP BY a.CustID, a.CategoryID, a.HyperParamsID)
                    AS v ON t.CustID = v.CustID AND t.CategoryID = v.CategoryID AND t.HyperParamsID = v.HyperParamsID
    SET 	t.Counter = v.Counter;

	DELETE d
	FROM Temp_PredictionStats AS t
		INNER JOIN Temp_PredictionData AS d ON t.CustID = d.CustID AND t.CategoryID = d.CategoryID
    WHERE t.Counter = 1 
		AND ((d.IsPreviousTruthWin IS NULL AND DATE_ADD(t.PredictDate, INTERVAL 15 DAY) > ip_ScanDate)
			OR (d.IsPreviousTruthWin IS NOT NULL AND DATE_ADD(t.PredictDate, INTERVAL 14 DAY) > ip_ScanDate)
            );
 
	INSERT IGNORE INTO SPU_AIML.WinlossPrediction(CustID, CategoryID, PredictDate, `Mode`, SuspiciousWinDay, SuspiciousLoseDay, IsPrediction, IsPredictWin, HyperParamsID)
	SELECT 	t.CustID
		, 	t.CategoryID
        ,	ip_ScanDate
        , 	t.`Mode`
        , 	t.SuspiciousWinDay
        , 	t.SuspiciousLoseDay
        ,	t.IsPrediction
        ,	t.IsPredictWin
        ,	t.HyperParamsID
    FROM Temp_PredictionData AS t;
	
    UPDATE SPU_AIML.WinlossPrediction AS a
		INNER JOIN Temp_PredictionData AS t ON t.CustID = a.CustID AND t.CategoryID = a.CategoryID AND t.HyperParamsID = a.HyperParamsID
    SET 	a.IsTruthWin = t.IsPreviousTruthWin
    WHERE a.PredictDate < ip_ScanDate 
		AND a.IsPrediction = 1
        AND a.IsTruthWin IS NULL;
    
    DROP TEMPORARY TABLE IF EXISTS Temp_PredictionData;
     
END$$

DELIMITER ;