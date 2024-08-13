<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head>
    <meta charset="UTF-8">
    <title>TimeCapsuleMap</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-light bg-light">
        <a class="navbar-brand" href="#">TimeCapsuleMap</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                <li class="nav-item active">
                    <a class="nav-link" href="timecapsule.php">home <span class="sr-only">(現在のページ)</span></a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="form.php">form</a>
                </li>
            </ul>
            </ul>
        </div>
    </nav>

    <div class="container">
        <h2>TimeCapsule入力フォーム</h2>
        <form action="" method="post">
            <div class="form-group">
                <label for="title">タイトル:</label>
                <input type="text" class="form-control" id="title" name="title" required>
            </div>
            <div class="form-group">
                <label for="message">メッセージ:</label>
                <textarea class="form-control" id="message" name="message" required></textarea>
            </div>
            <div class="form-group">
                <label for="latitude">緯度:</label>
                <input type="text" class="form-control" id="latitude" name="latitude" required>
            </div>
            <div class="form-group">
                <label for="longitude">経度:</label>
                <input type="text" class="form-control" id="longitude" name="longitude" required>
            </div>

            <div class="form-group">
                <label for="end_datetime">終了日時:</label>
                <input type="datetime-local" class="form-control" id="end_datetime" name="end_datetime" required>
            </div>
            <button type="submit" class="btn btn-primary">登録</button>
        </form>
        <?php
        if ($_SERVER['REQUEST_METHOD'] == 'POST') {
            $title = $_POST['title'];
            $message = $_POST['message'];
            $latitude = $_POST['latitude'];
            $longitude = $_POST['longitude'];
            $location = "ST_SetSRID(ST_MakePoint($longitude, $latitude), 4326)";
            $end_datetime = $_POST['end_datetime'];

            $query = "INSERT INTO time_capsule (title, message, location, end_datetime) 
                VALUES ('$title', '$message', $location, '$end_datetime')";

            $conn = pg_connect("host=localhost dbname=s2322098 user=s2322098 password=6LFVR4pU") or die('Could not connect: ' . pg_last_error());
            $result = pg_query($conn, $query) or die('Query failed: ' . pg_last_error());
            if ($result) {
                echo "<div class='alert alert-success'>データが正常に登録されました。</div>";
            } else {
                echo "<div class='alert alert-danger'>エラー: " . pg_last_error() . "</div>";
            }
        
            pg_close($conn);
        }
        ?>
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
