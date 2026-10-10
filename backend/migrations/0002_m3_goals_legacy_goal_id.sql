-- m3_goals.legacy_goal_id -- bridge column linking each m3 goal mirror to the
-- legacy `goals` row it was copied from (app/services/m3_bridge.py).
--
-- Idempotent: safe to run against a fresh DB that already got the schema from
-- ORM create_all/init_db (the column now exists on the model too), and against
-- an existing DB that hasn't been migrated yet.

SET @ddl := (
    SELECT IF(
        COUNT(*) = 0,
        'ALTER TABLE `m3_goals` ADD COLUMN `legacy_goal_id` INTEGER NULL',
        'SELECT 1'
    )
    FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'm3_goals' AND column_name = 'legacy_goal_id'
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @ddl := (
    SELECT IF(
        COUNT(*) = 0,
        'CREATE INDEX ix_m3_goals_legacy_goal_id ON `m3_goals` (`legacy_goal_id`)',
        'SELECT 1'
    )
    FROM information_schema.statistics
    WHERE table_schema = DATABASE() AND table_name = 'm3_goals' AND index_name = 'ix_m3_goals_legacy_goal_id'
);
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;