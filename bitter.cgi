#!/usr/bin/perl -w

# written by Rachit Jain (z5088424@student.unsw.edu.au) October 2015
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/bitter/
use File::Basename;
use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
use Cwd;
use CGI::Session;
use CGI;
$CGI::POST_MAX =1024*5000;
use lib '.';
use HTTP::Cookies;
use Date::Parse;
use File::Path 'rmtree';
warningsToBrowser(1);
# print start of HTML ASAP to assist debugging if there is an error in the script
print <<eof;
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
	<title>Bitter</title>
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">
</head>
<body bsckgroud="coffee.jpg">
eof
# some globals used through the script
$debug = 1;
$dataset_size = "medium"; 
$users_dir = "dataset-$dataset_size/users";
$username = param("username") || "";
$authentication=0;
$cgi = new CGI;
$session = new CGI::Session("driver:File", undef, {Directory=>"/tmp"});
$session->clear if $cgi->param('logout');
#for logging in
print <<eof;
    <form class= "form-inline" role ="form" method="post" action="">
		<div class="form-group">
			<label for="username">Username: </label>
			<input name="username"value=""type="text" class="form-control" placeholder="Enter username"> 
		</div>
		<div class="form-group">
			<label for="password">Password: </label>
			<input name="password" value=""type="password" class="form-control" placeholder="Enter Password">
		</div>
		<input class="btn btn-default" data-toggle="tooltip" title ="Login" type="submit" name="login_button" value="Login">
		<input type="submit" class="btn btn-default"value="Register for free" name="register">
		<input type="submit" class="btn btn-default"value="Can't access your account" name="forgot_password">
eof
print hidden('username');
print "<br>";
############################---------New User------------#############################3
if(defined param('register'))
{	
	print <<eof;
	<form role="form"method ="post" action="">
	Name: <input type ="text" name="new_name"><br><br>
	Username: <input type ="text" name="new_username"><br><br>
	Password: <input type ="text" name="new_password"><br><br>
	Email: <input type ="text" name="new_email"><br><br>
	Home Suburb: <input type = "text" name="new_home"><br><br>
	<input type="submit" name="register_submit" value="Submit" class="btn btn-default"><br><br>
eof
}
if(defined param('register_submit'))
{
	new_user();
	print<<eof;
	<div class="alert alert-success">Thanks for registering. You can now login here
	</div>
	<form method = "post" action="http://cse.unsw.edu.au/~z5088424/ass2/bitter.cgi"><br>
	<input class="btn btn-default"type="submit" name="new_login" value="Login Here">
eof
}
sub new_user
{
	$new_name=param('new_name');
	$new_password=param('new_password');
	$new_email=param('new_email');
	$new_home=param('new_home');
	$new_username= param('new_username');
	mkdir "$users_dir/$new_username" or die "cant make new directory $new_username: $!";
#	open FIL, ">>$users_dir/$new_username/bleats.txt" or die "cant open $new_username/bleats.txt: $!";
	close FIL;
	open F, ">>$users_dir/$new_username/details.txt" or die "cant open $new_username/deatils.txt: $!";
	print F "full_name: $new_name\n";
	print F "username: $new_username\n";
	print F "password: $new_password\n";
	print F "email: $new_email\n"; 
	print F "home_suburb: $new_home\n";
	close F;
}
#############################----------LOGIN-------------#################################
if(defined param("login_button"))
{
	login();
	param('user', $username);
    print hidden ('user');
}
sub login
{	#my $username_found=0;
	$username = param("username") || "";
    $password = param("password") || "";
    opendir (DIR, $users_dir) or die "cant open $users_dir: $!";
    while($original_name = readdir(DIR))
    {
        if($original_name eq $username)
        { 	$username_found=1;
            print "<br>";
            open FIL, "<$users_dir/$original_name/details.txt" or die "cant open $username: $!";
            while ($line = <FIL>)
            {
                if($line =~ /^password/)
                {
                    $line =~ s/password://g;
                    $line =~ s/ //g;
                    chomp $line;
                    if($line eq param('password'))
                    {
                        $authentication = 1;
						param('authentication', $authentication);
						print hidden ('authentication');
                    }
                    else
                    {
                         print<<eof;
						 <div class ="alert alert-danger">Sorry! That password is incorrect</div>
eof
                    }
                }
            }
            close FIL;
        }
    }
    closedir DIR;
	if($username_found == 0)
	{	
		 print<<eof;
		 <div class ="alert alert-danger">Sorry! Username doesn't exists</div>
eof
	}
}
################################---------After Logging in --------------###################
if($authentication == 1)
{
   logout_screen();
   #for search
    print<<eof;
    <form method="post" action="" class="navbar-form">
		<div class="form-group">
			<input type="submit" class="btn btn-default"name="edit_info" value="Edit Information">
    		<input type="text" class ="form-control" name="search_field" placeholder="Search for a user"> 
			<input class="btn btn-default" type="submit" value="Search" name="search_button"> 
	<input type ="text" name="bleat_textbox" placeholder="Share something!"> <input type ="submit" class="btn btn-default" value="Send Bleat" name="send_bleat_button">
		</div>
	<input type ="text" name="bleat_search_textbox" placeholder="Search for a particular bleat"> 	
	<input type ="submit" class="btn btn-primary"name = "search_bleat_byword" value = "Go!">
	<input type="submit" class="btn btn-default" name ="browse" value="Browse">
	<input type="submit" class="btn btn-default" name ="delete_bleats" value="Delete Bleats">
eof
	$bleat_search1 = param('bleat_search_textbox');
	param("search_bleat", $bleat_search1);
	print hidden ('search_bleat');
	print "<h3>Your News Feed</h3>";
	print recent();
	print hidden ('user');	
	#cookie_check();


}
sub cookie_check
{
	$q = new CGI;
	$session = new CGI::Session("driver:File", undef, {Directory=>"/tmp"});
	$sid= $session->id();
	return $sid;
	#$cookie = $q->cookie( -name => $session->name, -value => $session->id );
	#print $q->header( -cookie=>$cookie);
 	#$sid= $q->cookie("CGISESSID") || undef;
	#print $sid;
	#$session = new CGI::Session(undef, $sid, {Directory=>'/tmp'});
	#print $session;
}

###############################----------Relevant Bleats-----########################
sub recent
{
	$user= param('user');
	open F1,"<$users_dir/$user/details.txt" or die "cant open deatils.txt in recent : $!";	
	while($line = <F1>)
	{
		if($line =~ /listens/)
		{
			$line =~ s/\blistens\b//g;
			$line =~ s/\://g;
			@users = split/\s+/, $line;
			print "|@users|";
			foreach $people (@users)
			{
				print "..$people..";
				$count_bleat=0;
				param('person_profile', $people);
				print hidden ('person_profile');
    			open F, "<$users_dir/$people/bleats.txt" or die "cant open $people/bleats.txt: $!";
        		my $all_bleats = 'dataset-medium/bleats';
        		$found=0;
        		while($user_bleat = <F>)
        		{
            		$user_bleat =~ s/" "//g;
            		chomp $user_bleat;
            		opendir (DIR, $all_bleats) or die "cant open $all_bleats: $!";
           			while( $file  = readdir(DIR))
            		{
                		chomp $file;
                		if($file eq $user_bleat)
                		{
                    		$found++;
                    		open Z, "<dataset-medium/bleats/$file" or die "cant open $file: $!";
                    		while($bleat = <Z>)
                    		{
									
									if($count_bleat<3)
									{
										if($bleat =~ /latitude/)
										{
										}
										elsif($bleat =~ /longitude/)
										{
										}
										elsif($bleat =~ /in_reply_to/)
										{
										}
										else
										{
											push(@bleat_array1, $bleat);
										}
									}	
                    		}
                    		close Z;
							$count_bleat++;
                		}
            		}
            		closedir(DIR);
        		}	
        		close F;
			}
		}
	}close F1;
	@bleat_array1 = reverse @bleat_array1;
	foreach $blea(@bleat_array1)
	{
		print "$blea<br>";
	}
}
#######################----------------------Browse---------#########################
if(defined param('browse'))
{
	print hidden('user');
	browse_users();
}
sub browse_users
{
	
	opendir(DIR, $users_dir);
	while ($person =readdir(DIR))
	{
		print<<eof;
		<input class="btn btn-link"type="submit" name="View Profile" value="$person">
		<br>
eof
	}
	closedir(DIR);

}

if(defined param('View Profile'))
{
	$user = param('View Profile');
	param('search_field', $user);
	print hidden('search_field');	
	param('user', $user);
	print hidden('user');
	search();
	$person_profile =~ /([username\:]+)\s*([a-zA-Z0-9]+)/;
    $person_profile = $2;
    param("person_profile", $person_profile);
    print hidden ('person_profile');
    open FILE, "<$users_dir/$user/details.txt" or die "cant open $user/details.txt :$!";
    while($line = <FILE>)
    {
        if($line =~ /(\blistens\b)+/)
        {
            @words = split /\s+/, $line;
        }

    }
    foreach $word (@words)
    {
        if($word eq $person_profile)
        {
            $listen_counter = 1;
        }
    }
    #for viewing bleats
    print "<br>";
    print <<eof;
    <form method ="post" action="">
    <input type = "submit" class="btn btn-default"name="view_bleats" value="View Bleats"> <input type="hidden" name="username" value="abc">
eof
    if($listen_counter ==1)
    {
        print<<eof
        <input type = "submit" class="btn btn-default"name = "unlisten" value = "Unfollow this user">
eof
    }

    elsif($listen_counter ==0)
    {
        print<<eof
        <input type = "submit"class="btn btn-default" name = "listen" value = "Follow this user">
eof
    }
}
#################-----------deleting bleats--------------_#####################
if(defined param('delete_bleats'))
{	
	print hidden ('user');
	delete_bleats();
	
}
sub delete_bleats
{
	$user= param('user');
	print hidden('user');
	open F, "<$users_dir/$user/bleats.txt" or die "cant open bleats.txt: $!";

        my $all_bleats = 'dataset-medium/bleats';
        $found=0;

        while($user_bleat = <F>)
        {
            $user_bleat =~ s/" "//g;
            chomp $user_bleat;
            opendir (DIR, $all_bleats) or die "cant open $all_bleats: $!";
            while( $file  = readdir(DIR))
            {
                chomp $file;
                if($file eq $user_bleat)
                {
                    $found++;
                    open Z, "<dataset-medium/bleats/$file" or die "cant open $file: $!";
                    print"--------------------------------------<br>";
					
                    while($bleat = <Z>)
                    {
                            if($bleat =~/in_reply_to/)
                            {
                                $bleat =~ /([in_reply_to\:]+)\s*([0-9]+)/;
                                $in_reply_bleat_number = $2;
                                view_reply_bleats($in_reply_bleat_number);
                                print "<br>";
                            }
                            else
                            {
                                push(@bleat_array, $bleat);
                                print "$bleat<br>";
                            }
                    }
					print<<eof;
					<input type="submit"class="btn btn-default" name="delete_this_bleat" value="delete $file"><br>
eof
                    close Z;
                }
            }
            closedir(DIR);
        }
        close F;
}
if(defined param('delete_this_bleat'))
{
	$bleat_num =  param("delete_this_bleat");
	$bleat_num =~ s/[a-zA-Z]+//g;
	$bleat_num=~ s/\s+//g;
	$user = param('user');
	open F, "<$users_dir/$user/bleats.txt" or die "cant open bleats.txt in delete_this_bleat: $!";
	@all_bleat_array = <F>;
	close F;
	foreach $bleat_num1 (@all_bleat_array)
	{
		chomp $bleat_num;
		chomp $bleat_num1;
		if($bleat_num1 eq $bleat_num)
		{
			  $bleat_num1=~ s/[0-9]+//g;
		}
	}
	open F, ">$users_dir/$user/bleats.txt" or die "cant open bleats.txt in delete_this_b
	     leat: $!";
	foreach $line (@all_bleat_array)
	{
		print F "$line\n";
	}
	close F;
}
###################------------Editting Information------############################
if(defined param('edit_info'))
{
	print hidden('user');
	print <<eof;
	<input type ="submit"class="btn btn-default" value="Edit Password" name="edit_pwd">
	<input type ="submit"class="btn btn-default" value="Edit Email" name="edit_email">
	<input type ="submit" value="Edit Home" class="btn btn-default"name="edit_home">
	<input type ="submit" value="Upload New Image" name="new_image_button"class="btn btn-default">
	<input type ="submit" value="Delete Account" name="delete_account"class="btn btn-default">
eof
}
############################-----------Uploading new images----------#################
if (defined param('new_image_button'))
{
	print hidden('user');
	print<<eof;
	<form action="" method ="post" enctype="multipart/form-data">
	<input type="file" name ="file">
	<input type="submit" name="upload_photo_button" value="Upload">
	</form>
eof
}
if (defined param('upload_photo_button'))
{
	$user= param('user');
	my $req = new CGI;
	print "fuck you ";	
	my $file = $req->param('file'); 
	my $file =~ /.*\."?(\w*)"?$/;
	open UPLOADFILE,">$users_dir/$user/pic2.jpg" or die "cant open pic1.jpg in image_upload: $!";
	while(read(param('file'),$buffer,1024))
	{
		print UPLOADFILE $buffer;
		
	}
	close F;
}

##############################----------------edit password----------#################
if(defined param('edit_pwd'))
{
	print hidden('user');
	print param('user');
	print<<eof;
	
	New Password: <input type="text" name="new_edit_password" value="">
	<input type="submit" name="submit_edit_password" value="Change"class="btn btn-default">
eof
}
if(defined param('submit_edit_password'))
{
	print hidden('user');
	edit_password();
	if($success==1)
	{
		print <<eof;
		<div class="alert alert-success">Password Changed</div>
eof
	}
	else 
	{
		print "Sorry, Your password couldn't be changed. Try Again later";
	}
}
sub edit_password
{
	$user= param('user');
	open F, "<$users_dir/$user/details.txt" or die "cant open $user/details.txt in edit_passowrd: $!";
	@details_array =<F>;
	foreach $line (@details_array)
	{
		if($line =~ /(\bpassword\b)+/)
		{
			$line = "password: ".param('new_edit_password')."\n";
			$success=1;
		}
	}
	close F;
	open F, ">$users_dir/$user/details.txt" or die "cant open $user/details.txt in edit_passowrd: $!";
	foreach $line1 (@details_array)
	{ 
		print F $line1;
	}
	return $success;
}
#####################################------edit home---------#######################3
if(defined param('edit_home'))
{
    print hidden('user');
    print<<eof;

    Home: <input type="text" name="new_edit_home" value="">
    <input type="submit" name="submit_edit_home" value="Change"class="btn btn-default">
eof
}
if(defined param('submit_edit_home'))
{
    print hidden('user');

    edit_home();
    print "Home Address changed!";
}
sub edit_home
{
    $user= param('user');
    open F, "<$users_dir/$user/details.txt" or die "cant open $user/details.txt in edit_home: $!";
    @details_array =<F>;
    foreach $line (@details_array)
    {
        if($line =~ /(\bhome_suburb\b)+/)
        {
            $line = "home_suburb: ".param('new_edit_home')."\n";
        }
    }
    close F;
    open F, ">$users_dir/$user/details.txt" or die "cant open $user/details.txt in edit_home: $!";
    foreach $line1 (@details_array)
    {
        print F $line1;
    }
}
##########################################----edit email id-----###############################
if(defined param('edit_email'))
{
    print hidden('user');
    print<<eof;

    New Email: <input type="text" name="new_edit_email" value="">
    <input type="submit" name="submit_edit_email" value="Change"class="btn btn-default">
eof
}
if(defined param('submit_edit_email'))
{
    print hidden('user');

    edit_email();
    print "Email ID Changed";
}
sub edit_email
{
    $user= param('user');
    open F, "<$users_dir/$user/details.txt" or die "cant open $user/details.txt in edit_email: $!";
    @details_array =<F>;
    foreach $line (@details_array)
    {
        if($line =~ /(\bemail\b)+/)
        {
            $line = "email: ".param('new_edit_email')."\n";
        }
    }
    close F;
    open F, ">$users_dir/$user/details.txt" or die "cant open $user/details.txt in edit_p    assowrd: $!";
    foreach $line1 (@details_array)
    {
        print F $line1;
    }
	close F;
}
################################--------Password Recovery-------#####################
if(defined param('forgot_password'))
{
	print <<eof;
	Enter all the details as asked:
	Username: <input type="text" value="" name="check_username">
	Email: <input type="text" value="" name="check_email">
	Home: <input type="text" value="" name="check_home">
	<input type="submit" class="btn btn-default"value="Submit" name="submit_forgot_password">

eof
}
if(defined param('submit_forgot_password'))
{
	forget_password();
}
sub forget_password
{	$count=0;
	print $user_name;
	$user_name = param('check_username');
	open F, "<$users_dir/$user_name/details.txt" or die "cant open details.txt in forget_password: $!";
	while($line  =<F>)
	{
		if($line =~ /(email)/)
        {
            $line =~ /([a-z\:\_]+)\s*([a-zA-Z@\.\s0-9]+)/;
			$email =$2;
			chomp $email;
			if($email eq param('check_email'))
			{
				$count++;
			}
        }
        if($line =~ /(home_suburb)/)
        {
            $line =~ /([a-z\:\_]+)\s*([a-zA-Z\s]+)/;
			$home = $2;
			chomp $home;
			if($home eq param('check_home'))
            {
                $count++;
            }
        }
	}
	close F;
	param('user_name', $user_name);
	print hidden('user_name');
	if($count == 2)
	{
		open F, "<$users_dir/$user_name/details.txt" or die "cant open details.txt in forget_password: $!";
		 print<<eof;

    	New Password: <input type="text" name="new_edit_password" value="">
    	<input type="submit" name="submit_edit_password1" value="Change"class="btn btn-default">
eof
	}
	else
	{
		print "Info supplied not correct";
		print $count;
	}	
}	

if(defined param('submit_edit_password1'))
{
	$user_name= param('user_name');
		param('user', $user_name);
		print hidden ('user');
    	edit_password();
   	 	if ($success==1)
		{
			print "Password Changed";
		}
}
################################-------------Deleting account----#####################
if(defined param('delete_account'))
{
	print hidden('user');
	print "Are you sure?";
	print<<eof;
	<input type = "submit" name="yes" value="yes"class="btn btn-default">
	<input type="submit" name="no" value="no"class="btn btn-danger">
eof
}
if(defined param('yes'))
{
	print hidden ('user');
	delete_account();
}
sub delete_account
{	
	$user= param('user');
	opendir(DIR, $users_dir) or die "cant open $users_dir in delete_account: $!";
	while($folder = readdir(DIR))
	{
		if($user eq $folder)
		{
			rmtree("$users_dir/$folder");
			if(-e $folder)
			{
				print "Sorry could'nt delete your account";
			}
			else
			{
				print "We will be glad if you come back";
			}
		}
	}
}
if(defined param('no'))
{
	print<<eof;
	<div class="alert alert-info">
	Thanks for being with us.
	</div>
eof
}
#################################---------Search----------###############################
if(defined param('search_button'))
{
	$final_found = 0;
	search();
	$user = param('user');
	$person_profile =~ /([username\:]+)\s*([a-zA-Z0-9]+)/;
	$person_profile = $2;
	param("person_profile", $person_profile);
	print hidden ('person_profile');
	open FILE, "<$users_dir/$user/details.txt" or die "cant open $user/details.txt :$!";
	while($line = <FILE>)
	{
		if($line =~ /(\blistens\b)+/)
		{
			@words = split /\s+/, $line;
		}
		
	}
	foreach $word (@words)
	{
		if($word eq $person_profile)
		{
		 	$listen_counter = 1;
		}
	}
	#for viewing bleats
	if($final_found ==1)
	{
	print "<br>";
	print <<eof;
	<form method ="post" action="">
	<input type = "submit" name="view_bleats" value="View Bleats"class="btn btn-default"> <input type="hidden" name="username" value="abc">
eof
	if($listen_counter ==1)
	{
		print<<eof
		<input type = "submit" name = "unlisten" value = "Unfollow this user"class="btn btn-default">
eof
	}
	
	elsif($listen_counter ==0) 
	{
		print<<eof
		<input type = "submit" name = "listen" value = "Follow this user"class="btn btn-default">
eof
	}
	}
}

sub search
{
    my $to_be_searched = param('search_field');
	print hidden('user');
    opendir (DIR, $users_dir) or die "cant open $users_dir: $!";

        while($original_name = readdir(DIR))
		{	
            if($original_name eq $to_be_searched)
            {   $user_found=1;
				$final_found=1;
                open F, "<$users_dir/$original_name/details.txt" or die "Cant open: $original_name $!";
                while($line = <F>)
                {
                    if($line =~ /username/)
                    {
                        $person_profile = $line;
                    }
                    if($line !~ /password/)
                    {
                        printing_format($line);
                    }
                }
                close F;

                if(open IMAGE, "<$users_dir/$to_be_searched/profile.jpg")
                {
                    print "<img src=\"$users_dir/$to_be_searched/profile.jpg\">\n<br>";
                    close IMAGE;
                }
            }
        }
        closedir (DIR);

		 if($user_found != 1)
        {
            opendir (DIR1, $users_dir) or die "cant open $users_dir: $!";
            while($original_name1 = readdir(DIR1))
            {
                open FIL, "<$users_dir/$original_name1/details.txt";# or die "Cant open: $original_name1 $!";
                while($line = <FIL>)
                {
                    if($line =~ /full_name/)
                    {
                        $line =~ /([full_name\:]+)\s+([a-zA-Z0-9\s+]+)/;
                        chomp $to_be_searched;
                        $full_name = $2;
                        chomp $full_name;
                        if($to_be_searched eq $full_name)
                        {	
							$fullname_found=1;
							$final_found =1;
                            param("person_profile", $personal_profile);
                            open FIL1, "<$users_dir/$original_name1/details.txt";# or die "Cant open: $original_name1 $!";
                            while($line1 = <FIL1>)
                            {
                                if($line1 =~ /username/)
                                {
                                    $person_profile = $line1;
                                }

                                printing_format($line1);
                            }
                            close FIL1;

                            if(open IMAGE, "<$users_dir/$original_name1/profile.jpg")
                             {
                                  print "<img src=\"$users_dir/$original_name1/profile.jpg\">";
                                  close IMAGE;
                             }

                        }
						else
						{
							$fullname_found =0;
						}
                    }
                }
                close FIL;
             }
             closedir (DIR1);
        }
		if($fullname_found == 0 && $user_found!=1)
		{
			opendir(DIR2, $users_dir) or die "cant open $users_dir";
			@username_array = readdir(DIR2);
			closedir(DIR2);

			foreach $user2 (@username_array)
			{
				if(index($user2 , $to_be_searched) != -1)
				{
					print<<eof;
					<input type="submit" class="btn btn-link" name ="View Profile" value="$user2";
					<br>
eof
				}
			}	
		}
		else
		{
			$substring_found=0;
		}
		if($fullname_found == 0 && $user_found!=1)
		{
			foreach $user3 (@username_array)
			{
				open F,"<$users_dir/$user3/details.txt";
				while ($line =<F>)
				{
					if($line =~ /full_name/)
					{
						$line =~ /([full_name\:]+)\s+([a-zA-Z0-9\s+]+)/;
						if(index($2 , $to_be_searched) != -1)
						{
							print<<eof;
							$2:<input type="submit" class="btn btn-link" name="View Profile" value="$user3">
eof
						}
					}
				}
				close F;
			}
		}
}

#######################################---------Sending Bleat-------####################3
if(defined param('send_bleat_button'))
{
	print hidden('user');
	send_bleat();
}
my (%a);
sub send_bleat 
{
	$the_user =  param('user');
    open FILE, ">>$users_dir/$the_user/bleats.txt" or die "Cant open $user_name: $!";
        my $r;
        do
        {

            $r = int (rand(10000));
        } until (!exists($a{$r}));
        print "Bleat sent!";
        print FILE $r . "\n";
        close FILE;
        open FILE1, ">>", "dataset-$dataset_size/bleats/$r" or die "cant open bleats : $!";
        print FILE1 "bleat: " .param('bleat_textbox'). "\n";
        print FILE1 "username: $the_user\n";
		print FILE1 "time: ". time."\n";
        close FILE1;

        $a{$r}++;
}
##################################---------Searching Bleat----------#####################
if(defined param('search_bleat_byword'))
{
	search_bleats();
}
sub search_bleats
{
	$bleat_search = param('bleat_search_textbox');
	opendir(DIR, "dataset-$dataset_size/bleats");
	while($file = readdir(DIR))
	{	
		open F, "<dataset-$dataset_size/bleats/$file";
		while($line = <F>)
		{
			if($line =~ /\b$bleat_search\b/)
			{
				open F1, "<dataset-$dataset_size/bleats/$file";
				print"---------------<br>";
				while($line1 = <F1>)
				{
					print "$line1<br>";
				}
				close F1;
			}
		}
		close F;
	}
	closedir(DIR);
}
##########################--------------listening to user--------###################
if(defined param('listen'))
{
	listen_user();
	print "You are now following $person_profile";
}
sub listen_user
{
	
	$user = param('user');
	
	$person_profile = param('person_profile');
	open F, "<$users_dir/$user/details.txt" or die"cant open $user in listen_user: $!";
	@array = <F>;
	foreach $line (@array)
	{	
		chomp $line;
		if($line =~ /(\blistens\b)+/)
		{
			$line .= " $person_profile";
		}
	}
	close F;
	open F, ">$users_dir/$user/details.txt" or die"cant open $user in listen_user: $!";
	foreach $line1 (@array)
	{
		print F $line1."\n";
	}
	close F;
}
######################------------Unlistening to users---------####################
if(defined param('unlisten'))
{
	unlisten_user();
	print "You are now unfollowing $person_profile";
}
sub unlisten_user
{
	$user = param('user');
	$person_profile = param('person_profile');
	open F, "<$users_dir/$user/details.txt" or die"cant open $user in unlisten_user: $!";
	@array = <F>;
	foreach $line (@array)
	{
		chomp $line;
		if($line =~ /(\blistens\b)+/)
		{
			$line =~ s/\b$person_profile\b//g;
		}
	}
	close F;
	open F, ">$users_dir/$user/details.txt" or die"cant open $user in listen_user: $!";
	foreach $line2 (@array)
	{
		print F $line2,"\n";
	}
	close F;
}
#############################-------------Viewing Bleat----------###################
sub view_reply_bleats($)
{
	  my $all_bleats1 = 'dataset-medium/bleats';
	 opendir (DIR1, $all_bleats1) or die "cant open $all_bleats1: $!";
	 while( $file1  = readdir(DIR1))
	 {
	 	 chomp $file1;
	 	 if($file1 eq $in_reply_bleat_number)
	     {	
		 	open Z1, "<dataset-medium/bleats/$file1" or die "cant open $file1: $!";
			print "In Reply to:<br>";
			while($bleat = <Z1>)
			{
				if($bleat=~ /in_reply_to/)
				{
					$bleat =~ /([in_reply_to\:]+)\s*([0-9]+)/;
					$in_reply_bleat_number = $2;
					#view_reply_bleats($in_reply_bleat_number);
				}
				else
				{
					push(@bleat_array, $bleat);
					#print <<eof;
				#	&nbsp &nbsp &nbsp &nbsp $bleat
				#	<br>
eof
				}
			}
		}
	}
}

		
if(defined param('view_bleats'))
{
	print hidden('user');
	viewbleats();
}
sub viewbleats 
{
	
	$personal_profile = param('person_profile');
	print "<br>";
	open F, "<$users_dir/$personal_profile/bleats.txt" or die "cant open bleats.txt: $!";

        my $all_bleats = 'dataset-medium/bleats';
        $found=0;

        while($user_bleat = <F>)
        {
            $user_bleat =~ s/" "//g;
            chomp $user_bleat;
            opendir (DIR, $all_bleats) or die "cant open $all_bleats: $!";
            while( $file  = readdir(DIR))
            {
                chomp $file;
                if($file eq $user_bleat)
                {
                    $found++;
                    open Z, "<dataset-medium/bleats/$file" or die "cant open $file: $!";
					#print"--------------------------------------<br>";
                    while($bleat = <Z>)
                    {
							if($bleat =~/in_reply_to/)
							{
								$bleat =~ /([in_reply_to\:]+)\s*([0-9]+)/;
								$in_reply_bleat_number = $2;
								#view_reply_bleats($in_reply_bleat_number);
								#print "<br>";
							}
							elsif($bleat =~/latitude/)
							{
							}
							elsif($bleat =~/longitude/)
							{
							}
							elsif($bleat =~ /username/)
							{
							}
							else
							{
								push(@bleat_array, $bleat);
						   		#print "$bleat<br>";
							}
                    }
                    close Z;
					push(@bleat_array,"-------------------------------------------------------------");
                }
            }
            closedir(DIR);
        }
        close F;
		@bleat_array = reverse @bleat_array;
		foreach $bleat (@bleat_array)
		{
			print "$bleat<br>";
		}

}
#######################_------------LogOut-----------------#########################
sub logout_screen
{
print<<eof;
<form method="post" action="">
<input type="submit" name ="logout" value="LogOut"class="btn btn-warning">
<br>
eof
}
if(defined param('logout'))
{
	$authentication=0;
	print<<eof;
	<div class="alert alert-success">Thanks for logging in!</div>
eof
}
##############################--------Printing Format-----------#######################
sub printing_format ($)
{
	$line = @_[0];
		if($line =~ /(full_name)/)
		{
			$line =~ /([a-z\:\_]+)\s*([a-zA-Z\s]+)/;
			print "Name: $2\n <br>";
		}
		if($line =~ /(home_latitude)/)
		{
	  		$line =~ /([a-z\:\_]+)\s*([0-9-\.]+)/;
			print "Home Latitude: $2 <br>";
        }
		
		if($line =~ /(listens)/)
		{
				$line =~ /([a-z\:]+)\s*([a-zA-Z0-9\s]+)/;
				print "Listens to: $2 <br>";
		}
		
		if($line =~ /(home_suburb)/)
		{
			$line =~ /([a-z\:\_]+)\s*([a-zA-Z\s]+)/;
			 print "Suburb: $2 <br>";
		}
		
		if($line =~ /(home_longitude)/)
		{
			$line =~ /([a-z\:\_]+)\s*([0-9\.]+)/;
			print "Home Longitude: $2 <br>";
		}
		
		if($line =~ /(user)/)
		{
			$line =~ /([a-z\:]+)\s*([a-zA-Z0-9]+)/;
		print "Username: $2 <br>";
		}
}

#
# HTML placed at bottom of every screen
#
sub page_header {
    return header,
        start_html("-title"=>"Bitter", -bgcolor=>"#000000", -text=>"#098E33"),
		
        center(h2(i("Bitter")));
}

#
# HTML placed at bottom of every screen
# It includes all supplied parameter values as a HTML comment
# if globalvariable $debug is set
#
sub page_trailer {
    my $html = "";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    return $html;
}
print<<eof;
</div>
</form>

</body>
</html>
eof

