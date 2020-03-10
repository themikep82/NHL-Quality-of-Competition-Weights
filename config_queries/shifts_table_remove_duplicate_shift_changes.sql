ALTER TABLE shifts
  ADD COLUMN shift_dupe_identifier TEXT;
  
UPDATE shifts
  SET shift_dupe_identifier = CONCAT(gameId, playerId, period, startTime::TEXT, endTime::TEXT);

DELETE FROM shifts
WHERE shiftId IN (SELECT shiftId
					FROM (
						SELECT shiftId,
						ROW_NUMBER() OVER( PARTITION BY shift_dupe_identifier
						ORDER BY shiftId) AS row_num
						FROM shifts ) temp
						WHERE temp.row_num > 1 );
        
ALTER TABLE shifts
  DROP COLUMN shift_dupe_identifier;