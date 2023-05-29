<?php
//$con=mysqli_connect("localhost","probins","gradox12","mach9store") or die(mysqli_error($con));
//$con=mysqli_connect("localhost","root","","store") or die(mysqli_error($con));

 $dbusername = "root"; 
    $dbpassword = "M3tsiT3ch123"; 
    $dbhost = "localhost"; 
    $dbname = "cloudbolt_demo"; 
	
	
	try 
    { 
	    $options = array(PDO::MYSQL_ATTR_INIT_COMMAND => 'SET NAMES utf8'); 
		global $pdo;
		$pdo = new PDO("mysql:host={$dbhost};dbname={$dbname};charset=utf8", $dbusername, $dbpassword, $options); 
		

    } 
    catch(PDOException $ex) 
    { 
        die("Failed to connect to the database: " . $ex->getMessage()); 
    } 
     
 $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION); 
 $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC); 


$result = $pdo->prepare("SELECT * FROM tbl_users");	

	
	$result->execute();
	$numrecords = $result->rowCount();
		//echo 'numrecords='.$numrecords.'<br>';
		if($numrecords > 0){
			$result_array = $result->fetchAll();
    			
		} else {
			
			$result_array = array();
		}






echo json_encode($result_array);

?>