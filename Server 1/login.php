<?php

    session_start();

    $current_user = null;
    $failed_login = false;

    if (isset($_POST['logout'])) {
        $_SESSION['current_user'] = null;
    }

    if (isset($_SESSION["current_user"])) {
        $current_user = $_SESSION["current_user"];
    }

    if (isset($_POST['username'])) {
        if ($_POST['username'] == "test") {
            $current_user = $_POST['username'];
            $_SESSION['current_user'] = $current_user;
        } else {
            $failed_login = true;
        }
    }
    

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <link rel="stylesheet" id="css-link">
    <title>Midnight Login Form</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link rel="preload" as="image" href="https://th.bing.com/th/id/R.c8b863d…?rik=Sd7niYPBaCOu6Q&riu=http%3a%2f%2fwww.pixelstalk.net%2fwp-content%2fuploads%2f2016%2f06%2fFree-Desktop-Starry-Night-Wallpaper-Images-Photos.jpg&ehk=hlsJKp9OG4aJ1FNGFGy%2f68d2Ew1RDBMgQF3ragciCoA%3d&risl=&pid=ImgRaw&r=0">
    <link
        href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;800&family=Roboto:wght@300;400;700;900&display=swap"
        rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"
        integrity="sha512-z3gLpd7yknf1YoNbCzqRKc4qyor8gaKU1qmn+CShxbuBusANI9QpRohGBreCFkKxLhei6S9CQXFEbbKuqLg0DA=="
        crossorigin="anonymous" referrerpolicy="no-referrer" />
</head>
<body>
    <div class="background"></div>
    <div class="wrapper">
        
        <div class="login-modal" id="main">
            <h1>Login</h3>
                <p id="notice" style="    text-align: center;
    color: rgb(255, 87, 87);
    display: none;
    position: absolute;
    width: inherit;
    margin-top: -6px;">Incorrect username or password</p>
            <form name="form" action="#" method="POST" onsubmit="return validate();">
                <label>Username</label>
                <input type="username" name="username" placeholder="Username">
                <i class="fa-solid fa-id-card"></i>
                <label>Password</label>
                <input type="password" name="password" placeholder="Password">
                <i class="fa-solid fa-lock"></i>
                <input type="submit" value="Login">
                
            </form>
        </div>

        <div class="login-modal" id="logged_in" style="display: none; height: 230px;">
            <h1>Logged in as "<?php echo($current_user);?>"</h3>
                <p id="notice-2" style="text-align: center;
                color: rgb(155, 155, 155);
                display: none;
                position: absolute;
                width: inherit;
                margin-top: -6px;">You are currently logged in</p>
            <form name="form" action="#" method="POST" onsubmit="return validate();">
                <input type="submit" name="logout" value="Log out">
            </form>
        </div>
    </div>
</body>
</html>
<script>
    function incorrect_error() {
        document.getElementById("notice").innerText = "Invalid username or password";
            document.getElementById("notice").style.display = "block";

            document.forms["form"]["username"].style.border = "1px solid #ff7f7f78";
            document.forms["form"]["password"].style.border = "1px solid #ff7f7f78";

            document.getElementsByClassName("background")[0].style.boxShadow = "inset 0 0 20px 12px #ff6666";

            setTimeout(function() {
                document.getElementsByClassName("background")[0].style.boxShadow = "inset 0 0 10px 12px #000000";
            }, 650);
    }

    function checkTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            // dark mode
            document.getElementById("css-link").setAttribute("href", "./themes/dark.css");
        } else {
            document.getElementById("css-link").setAttribute("href", "./themes/light.css");
        }
    }

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
        const newColorScheme = event.matches ? "dark" : "light";
        checkTheme();
    });

    checkTheme();

    <?php if ($failed_login) { ?>

        incorrect_error();
    
    <?php } elseif ($current_user != null) {?>

        document.getElementById("main").style.display = "none";
        document.getElementById("logged_in").style.display = "block";
        document.getElementById("notice-2").style.display = "block";

    <?php } ?>



</script>