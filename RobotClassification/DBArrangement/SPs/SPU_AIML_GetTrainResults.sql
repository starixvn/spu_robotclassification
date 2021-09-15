DROP PROCEDURE IF EXISTS `SPU_AIML_GetTrainResults`;

DELIMITER $$
CREATE DEFINER=`AIMLOwner`@`%` PROCEDURE `SPU_AIML_GetTrainResults`(
	IN 	ip_CustCategoryData		JSON,
    IN  ip_HyperParamsID		SMALLINT UNSIGNED,
    
    OUT op_ErrorMessage 		VARCHAR(200)
)
    SQL SECURITY INVOKER
BEGIN
	/*
		Created:	20210422@Long.Luu
		Task:		Get data from Train Results [Redmine ID: #0000]
		DB:			SPU_AIML
		Original: 

		Revisions:
			- 20210422@Long.Luu: Created [Redmine ID: #0000]
            
		Example:
			call SPU_AIML.SPU_AIML_GetTrainResults ('[{"C": 43600693, "CAT": 1}]',1,@msg);    
	*/ 

    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN         
        GET DIAGNOSTICS CONDITION 1 op_ErrorMessage = MESSAGE_TEXT;
    END;
    
    DROP TEMPORARY TABLE IF EXISTS Temp_CustCategory;    
	CREATE TEMPORARY TABLE Temp_CustCategory 
    (	 
			CustID			BIGINT UNSIGNED	NOT NULL
		, 	CategoryID		TINYINT UNSIGNED NOT NULL
        , 	PRIMARY KEY	    PK_Temp_CustCategory(CustID,CategoryID) 
    );      
    
    INSERT INTO Temp_CustCategory(CustID, CategoryID)
	SELECT 	tmpTable.CustID
		, 	tmpTable.CategoryID
	FROM JSON_TABLE(ip_CustCategoryData,
		 "$[*]" COLUMNS(
			  CustID 				BIGINT UNSIGNED		PATH "$.C"
			, CategoryID			TINYINT UNSIGNED	PATH "$.CAT"
		 )) AS tmpTable;  
    
    SELECT 	r.CustID
		, 	r.CategoryID
        , 	r.`Mode`
        , 	r.SuspiciousWinDay
        , 	r.SuspiciousLoseDay
        ,	r.Streak
        ,	r.ActiveDay
    FROM SPU_AIML.TrainResults AS r
		INNER JOIN Temp_CustCategory AS t ON r.CustID = t.CustID AND r.CategoryID = t.CategoryID
	WHERE r.HyperParamsID = ip_HyperParamsID;
    
    DROP TEMPORARY TABLE IF EXISTS Temp_TrainResults;
     
END$$

DELIMITER ;