<html>
    <head>
        <link type="text/css" rel="stylesheet" href="static/jqueryFileTree.css">
        <style>
            .alignright{
                float:right;
            }
            .alignleft{
                float:left;
            }
        </style>
        <script type="text/javascript" src="static/jquery.js"></script>
        <script type="text/javascript" src="static/jqueryFileTree.js"></script>
        <script type="text/javascript">
        var curr_dir = "{{root}}";
        var owner = "{{owner}}";
        $(document).ready( function(){
            $("#browser").fileTree({ "root":"{{root}}", "script":"listdir","multiFolder":false },function(file){
                window.open("/download/"+encodeURIComponent(file));
            });
            
        });
        
        </script>
    </head>
    <body>
        <h1 class="Title">{{owner}}'s Files</h1>
        <h3>Showing : {{root}}<br><a href="/?path=/" style="text-decoration=none;">Goto {{owner}}'s shared root </a></h3>
        <br>
        <div id="browser"></div>
    </body>
</html>
