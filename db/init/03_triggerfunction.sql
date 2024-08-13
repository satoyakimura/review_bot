CREATE OR REPLACE FUNCTION delete_old_reviews()
RETURNS TRIGGER AS $$
BEGIN
    -- 現在の日付から1ヶ月以上前のレコードを削除
    DELETE FROM review
    WHERE start_time < NOW() - INTERVAL '1 month';
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER cleanup_old_reviews
AFTER INSERT OR UPDATE ON review
FOR EACH STATEMENT
EXECUTE FUNCTION delete_old_reviews();
