var USER_INFO;
var skip;
var count;
var MAX_RES=20;
var query;

function get_info_and_update()
{
    $.getJSON("users",function(result){
                    $("#user_table tbody").empty();
                    $.each(result,function(i,user_info){
                        USER_INFO[user_info.name] = user_info.address;
                        var str="<tr><td class=\""+user_info.status+"\">"
                        str += "<a href=\""+user_info.address+"\" target=\"_blank\">"+
                                   user_info.name+"</a></td>";
                        str += "<td>"+user_info.delta+" ago</td></tr>";
                        
                        $('#user_table tbody').append(str); 
                    });
                });
}

function search_it(){
    count = 0;
    $.getJSON("search",{'query':query,'skip':skip},function(result){
            $("#results").empty();
            if (result.success){
                write_status("Success..");
                $.each(result.data,function(i,entry){
                    var user=entry[0];
                    var path=entry[1];
                    var str = "<tr><td><a href=\""+USER_INFO[user]+"/?path="+escape(path)+"\" target=\"_blank\">";
                    str += path + "</a></td>";
                    str += "<td>"+user+"</td></tr>";
                    $('#results').append(str);
                    count += 1;
                });
                append_status(" "+count+" Results found");
                page += 1;
                skip += count;
                
                $('#prev').text((page-1)+" <<");
                $('#next').text(">> "+(page+1));
                
                
            }
            else{
                write_status("No results found");
            }
            if (page > 1){
                    enable('#prev');
                }
                else{
                    disable('#prev');
                }
                if (count < MAX_RES){
                    disable('#next');
                }
                else{
                    enable('#next');
                }
            
        });
}
function do_search(){
    disable('#next,#prev');
    skip = 0;
    page = 0;
    write_status("Searching ...")
    query=$("#query").val();
    search_it();
}

function get_prev(){
   skip = skip - count - MAX_RES;
   page -= 2;
   search_it();
}

function get_next(){
    search_it();
}
 
function write_status(stat){
    $("#status").empty().text(stat);
}

function append_status(stat){
    orig=$("#status").text();
    $("#status").text(orig+stat);
}

function disable(str){
    $(str).attr("disabled","disabled");
}

function enable(str){
    $(str).removeAttr("disabled");
}

$(document).ready(function(){
            USER_INFO = new Object();
            $.ajaxSetup({'cache':false})
            get_info_and_update();
            disable('#next,#prev');
            setInterval(get_info_and_update,60000);
                  
        });



