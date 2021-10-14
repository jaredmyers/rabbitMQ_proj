<?php
  include_once 'dbh.inc.php';
?>

<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="Mark Otto, Jacob Thornton, and Bootstrap contributors">
    <meta name="generator" content="Hugo 0.88.1">
    <title>Signin · IT490</title>

    <link rel="canonical" href="https://getbootstrap.com/docs/5.1/examples/sign-in/">

    

    <!-- Bootstrap core CSS -->
<!---<link href="/docs/5.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
<!-- CSS only -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    <!-- Favicons -->
<!--<link rel="apple-touch-icon" href="/docs/5.1/assets/img/favicons/apple-touch-icon.png" sizes="180x180">
<link rel="icon" href="/docs/5.1/assets/img/favicons/favicon-32x32.png" sizes="32x32" type="image/png">
<link rel="icon" href="/docs/5.1/assets/img/favicons/favicon-16x16.png" sizes="16x16" type="image/png">
<link rel="manifest" href="/docs/5.1/assets/img/favicons/manifest.json">
<link rel="mask-icon" href="/docs/5.1/assets/img/favicons/safari-pinned-tab.svg" color="#7952b3">
<link rel="icon" href="/docs/5.1/assets/img/favicons/favicon.ico">-->
<meta name="theme-color" content="#7952b3">


    <style>
      .bd-placeholder-img {
        font-size: 1.125rem;
        text-anchor: middle;
        -webkit-user-select: none;
        -moz-user-select: none;
        user-select: none;
      }

      @media (min-width: 768px) {
        .bd-placeholder-img-lg {
          font-size: 3.5rem;
        }
      }
    </style>

    
    <!-- Custom styles for this template -->
    <link href="signin.css" rel="stylesheet">
  </head>
  <body class="text-center">
    
<main class="form-signin">
  <form method="post">
    <!---<img class="mb-4" src="" alt="" width="72" height="57">-->
    <h1 class="h3 mb-3 fw-normal">Please sign in</h1>

    <div class="form-floating">
      <input type="text" class="form-control" id="floatingInput" placeholder="Account Name" name="account">
      <label for="floatingInput">Account</label>
    </div>
    <div class="form-floating">
      <input type="password" class="form-control" id="floatingPassword" placeholder="Password" name="pw">
      <label for="floatingPassword">Password</label>
    </div>

    <div class="checkbox mb-3">
      <label>
        <input type="checkbox" value="remember-me"> Remember me
      </label>
    </div>
    <button class="w-100 btn btn-lg btn-primary" value="submit" name="submit" type="submit">Sign in</button>
    <p class="mt-5 mb-3 text-muted">&copy; 2021</p>
  </form>
</main>

<?php

if (isset($_POST["submit"])){

#var_dump($GLOBALS);

# Establish input variables

$accountName = $_POST['account'];
#$lastname = $_POST['lname'];
#$floristID = $_POST['ident'];
$password = $_POST['pw'];
#$phone = $_POST['phone'];
#$dropDown = $_POST['dropDown'];

	#echo $accountName . " " . $password . " ";

# checks if the customer ID returned a row in the database
# if it did, the id is valid, then compares input names to database names
# if all matches, then is customer, execute action
# if either names dont match ID, or ID doesn't return a row, customer doesn't exit

$sqlCheck = "SELECT account_name, pw FROM site_login WHERE account_name = '$accountName';";
$result = mysqli_query($conn, $sqlCheck);

if(mysqli_num_rows($result) > 0){

  $row = mysqli_fetch_assoc($result);
  $values = array_values($row);
  
  #echo $values[0] . "<0 " . $values[1] . "<1 " . $values[2] . "<2 " . $values[3] . "  ";

  $acc = $values[0];
  #$last = $values[2];
  $pass = $values[1];
  #$phone = $values[4];

  if($acc == $accountName && $pass == $password){
    echo '<script> alert("You logged in!")</script>';
    #pager($dropDown);	


  } else {
    
    echo '<script> alert("Your credentials do not match my guy. ngmi")</script>';
  }

} else {

  echo '<script> alert("You dont even exist my dude, get rekt")</script>';
}


}




?>


    
  </body>
</html>
