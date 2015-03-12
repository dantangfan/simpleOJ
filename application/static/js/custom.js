//  Author: Louis Holladay
//  Website: AdminDesigns.com
//  Last Updated: 01/01/14 
// 
//  This file is reserved for changes made by the user 
//  as it's often a good idea to seperate your work from 
//  the theme. It makes modifications, and future theme
//  updates much easier 
// 

//  Place custom styles below this line 
///////////////////////////////////////
var window_height = $(window).height();
var main_height = $('#main').height();
var content_height = $('#content').height();
if (window_height - 106 > content_height) {
    //$('#main').css("height", window_height - 53);
    //$('#content').css("height", window_height-106);
} 
$('#content').css('min-height', window_height-106);
var HJ_username = "";

var HJ = function () {
    $.getJSON("/user/login_status", function(data){
        if(data.login_status == false){
            $('#user-area').append("<button class='btn btn-primary btn-gradient' id='btn-login-form'><i class='fa fa-keyboard-o'></i><b>&nbsp;Login</b></button>");
            $('#user-area').append("<a href='/register' style='margin-left:20px;font-size:16px;'>register</a>");
            $('#btn-login-form').click(function () {
                $.get('/user/login_form', function(data){
                    if(!$('#LoginModal').length){
                        $('body').append(data);
                        $('#btn-login').click(function(){
                        $.ajax({
                            cache: true,
                            type: "POST",
                            url:"/user/login",
                            data:$('#loginForm').serialize(),
                            async: true,
                            error: function(request) {
                                alert("Connection error");
                            },
                            success: function(data) {
                                data = $.parseJSON(data);
                                
                                if(data.result == 'ok'){
                                    var username = data.username;
                                    if(username.indexOf("_HJ_")>=0){
                                        username = username.replace('_HJ_', "");
                                    }
                                    alert("Dear " + username + ", welcome back!");
                                    window.location.href=window.location.href;
                                }else{
                                    alert("Username or Password does not match!");
                                }
                            }
                        });

                    });
                    }
                    $('#LoginModal').modal();
                });
            });
        }
        else{
            HJ_username = data.username;
            var email_hash = data.email_hash;
            $('#user-area').append("<div class=\"btn-group user-menu\" id=\"menu_user\"><button type=\"button\" class=\"btn btn-default btn-gradient btn-sm dropdown-toggle\" data-toggle=\"dropdown\"> <span id=\"menu-user-icon\" class=\"glyphicons glyphicons-user\"></span> <b id='menu-user-username'></b> </button><button type=\"button\" class=\"btn btn-default btn-gradient btn-sm dropdown-toggle padding-none\" data-toggle=\"dropdown\"> <img src=\"http://gravatar.duoshuo.com/avatar/" + email_hash +"?d=mm\" alt=\"user avatar\" width=\"28\" height=\"28\"> </button><ul class=\"dropdown-menu checkbox-persist animated-short animated flipInY\" role=\"menu\"><li class=\"menu-arrow\"><div class=\"menu-arrow-up\"></div></li><li class=\"dropdown-header\">Your Account <span class=\"pull-right glyphicons glyphicons-user\"></span></li><li><ul class=\"dropdown-items\"><li><div class=\"item-icon\"><i class=\"fa fa-envelope-o\"></i> </div><a class=\"item-message\" href=\"setting\">Setting</a> </li><li><div class=\"item-icon\"><i class=\"fa fa-envelope-o\"></i> </div><a class=\"item-message\" id='btn-logout' href=\"\">Logout</a> </li></li></ul></li></ul></div>");
            $('#menu-user-username').text(data.username);
            $('#btn-logout').click(function(){
                $.getJSON("/user/logout", function(data){
                    if(data.result == "ok"){
                        alert("You are now logged out.");
                        window.location.href = '/';
                    }
                });
                return false;
            });
            var username = $('#menu-user-username').text();
            if(username.indexOf("_HJ_")>=0){
                username = username.replace('_HJ_', "<img src='/static/img/logos/hj-small.png' style='height: 15px;'>&nbsp;");
                $('#menu-user-username').html(username);
                $('#menu-user-icon').remove();
            }
        }
    });
}



