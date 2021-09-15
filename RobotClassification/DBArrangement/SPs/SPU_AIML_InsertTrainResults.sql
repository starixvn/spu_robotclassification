DROP PROCEDURE IF EXISTS `SPU_AIML_InsertTrainResults`;

DELIMITER $$
CREATE DEFINER=`AIMLOwner`@`%` PROCEDURE `SPU_AIML_InsertTrainResults`(
	IN 	ip_TrainedData 		JSON,
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
			call SPU_AIML.SPU_AIML_InsertTrainResults ('[{"C": 43600693, "CAT": 1, "M": 5.1, "SWD": 5, "SLD": 2, "STR": 1, "AD": 69, "PID":1, "OBC":0.5, "OTO":0.1, "IBC":0.3, "ITO":0.9}]','2021-04-22',@msg);    
	*/ 

    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN         
        GET DIAGNOSTICS CONDITION 1 op_ErrorMessage = MESSAGE_TEXT;
    END;
    
    DROP TEMPORARY TABLE IF EXISTS Temp_TrainResults;    
	CREATE TEMPORARY TABLE Temp_TrainResults 
    (	 
			CustID						BIGINT UNSIGNED	NOT NULL
		, 	CategoryID					TINYINT UNSIGNED NOT NULL
		, 	`Mode`						DECIMAL(10,4) NOT NULL
		, 	SuspiciousWinDay			DECIMAL(15,4) NOT NULL
		, 	SuspiciousLoseDay			DECIMAL(10,4) NOT NULL
        , 	Streak						SMALLINT NOT NULL
        , 	ActiveDay					INT UNSIGNED NOT NULL
        ,	IsNewCouple					BIT DEFAULT 1
        ,	HyperParamsID				SMALLINT UNSIGNED
		,	OutstandingBC				DECIMAL(6,4) NULL
		,	OutstandingTO				DECIMAL(6,4) NULL
		,	InternalBC					DECIMAL(6,4) NULL
		,	InternalTO					DECIMAL(6,4) NULL
        , 	PRIMARY KEY	    PK_Temp_TrainResults_CustID_CategoryID(CustID,CategoryID) 
    );      
    
    INSERT INTO Temp_TrainResults(CustID, CategoryID, `Mode`, SuspiciousWinDay, SuspiciousLoseDay, Streak, ActiveDay, HyperParamsID, OutstandingBC, OutstandingTO, InternalBC, InternalTO)
	SELECT 	tmpTable.CustID
		, 	tmpTable.CategoryID
		, 	tmpTable.`Mode`
        , 	tmpTable.SuspiciousWinDay
        , 	tmpTable.SuspiciousLoseDay
        , 	tmpTable.Streak
        ,	tmpTable.ActiveDay
        ,	tmpTable.HyperParamsID
        , 	tmpTable.OutstandingBC
        , 	tmpTable.OutstandingTO
        ,	tmpTable.InternalBC
        ,	tmpTable.InternalTO
	FROM JSON_TABLE(ip_TrainedData,
		 "$[*]" COLUMNS(
			  CustID 				BIGINT UNSIGNED		PATH "$.C"
			, CategoryID			TINYINT UNSIGNED	PATH "$.CAT"
			, `Mode`				DECIMAL(10,4)		PATH "$.M"
            , SuspiciousWinDay		DECIMAL(15,4)		PATH "$.SWD"
            , SuspiciousLoseDay		DECIMAL(10,4)		PATH "$.SLD"
            , Streak				SMALLINT 			PATH "$.STR"
            , ActiveDay				INT UNSIGNED		PATH "$.AD"
            , HyperParamsID			SMALLINT UNSIGNED	PATH "$.PID"
			, OutstandingBC			DECIMAL(6,4)		PATH "$.OBC"
			, OutstandingTO			DECIMAL(6,4)		PATH "$.OTO"
			, InternalBC			DECIMAL(6,4)		PATH "$.IBC"
			, InternalTO			DECIMAL(6,4)		PATH "$.ITO"
		 )) AS tmpTable;  
    
    SET SQL_SAFE_UPDATES = 0;
    UPDATE Temp_TrainResults AS t
		LEFT JOIN SPU_AIML.TrainResults AS a ON t.CustID = a.CustID 
			AND t.CategoryID = a.CategoryID AND t.HyperParamsID = a.HyperParamsID
	SET t.IsNewCouple = 0
    WHERE a.CustID IS NOT NULL
		AND a.CategoryID IS NOT NULL;
        
	INSERT IGNORE INTO SPU_AIML.TrainResults(CustID, CategoryID, `Mode`, SuspiciousWinDay, SuspiciousLoseDay, Streak, ActiveDay, LastScannedDate, HyperParamsID, OutstandingBC, OutstandingTO, InternalBC, InternalTO)
	SELECT 	t.CustID
		, 	t.CategoryID
        , 	t.`Mode`
        , 	t.SuspiciousWinDay
        , 	t.SuspiciousLoseDay
        ,	t.Streak
        ,	t.ActiveDay
        ,	ip_ScanDate
        ,	t.HyperParamsID
        ,	t.OutstandingBC
        , 	t.OutstandingTO
        , 	t.InternalBC
        , 	t.InternalTO
    FROM Temp_TrainResults AS t
	WHERE IsNewCouple = 1;
	
    UPDATE SPU_AIML.TrainResults AS a
		INNER JOIN Temp_TrainResults AS t ON t.CustID = a.CustID AND t.CategoryID = a.CategoryID AND t.HyperParamsID = a.HyperParamsID
    SET 	a.`Mode` = t.`Mode`
		,	a.SuspiciousWinDay = t.SuspiciousWinDay
        ,	a.SuspiciousLoseDay = t.SuspiciousLoseDay
        ,	a.Streak = t.Streak
        ,	a.ActiveDay = t.ActiveDay
        ,	a.OutstandingBC = t.OutstandingBC
        , 	a.OutstandingTO = t.OutstandingTO
        , 	a.InternalBC = t.InternalBC
        , 	a.InternalTO = t.InternalTO
        , 	a.LastScannedDate = ip_ScanDate
    WHERE t.IsNewCouple = 0;
    
    DROP TEMPORARY TABLE IF EXISTS Temp_TrainResults;
     
END$$

DELIMITER ;