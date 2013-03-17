function size_format (filesize) {
    if (filesize >= 1073741824) {
        filesize = number_format(filesize / 1073741824, 2, '.', '') + ' Gb';
    } else {
        if (filesize >= 1048576) {
        filesize = number_format(filesize / 1048576, 2, '.', '') + ' Mb';
        } else {
            if (filesize >= 1024) {
                filesize = number_format(filesize / 1024, 0) + ' Kb';
            } else {
            filesize = number_format(filesize, 0) + ' bytes';
          };
      };
    };
    return filesize;
 };
 
function disable(str){
    $(str).attr("disabled","disabled");
}

function enable(str){
    $(str).removeAttr("disabled");
}

function goto(path){
    $.getJSON("browse",{"path":path},function(data){
            $("#browser_table tbody").empty();
            $.each(data.dirs,function(i,dirname){
                $("#browser_table tbody").append("<div class=\"directory\"\
                 path=\""+path+"/"+"dirname"+"\">")
                    
            });
            
    });
}
 $(document).ready(function(){
            goto(curr_dir);
   
        });
