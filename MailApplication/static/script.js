$("#compose-actions").hide();

$(document).ready(function(){
  $("#compose-button").click(function(){
    $("#inbox-actions").hide();
    $("#compose-actions").show();
  });
});


$("#send_btn").on("click", function() {
try{
  let receiver_mail = $("#receiver_mail").val();
  let mail_subject = $("#mail_subject").val();
  let mail_content = CKEDITOR.instances['mail_content'].getData();
  $.ajax({
      url: '/send_mail',
      data: {"receiver_mail": receiver_mail, "mail_subject": mail_subject, "mail_content": mail_content},
      method: "POST",
      success: function(data) {
          location.reload();
      }
    });
}
catch(err){
    alert(err)
}
});

function open_mail(mail_id){
    mails = document.getElementById('inbox-actions').style.display = 'none';
    mail_desc = document.getElementById('full-mail-details').style.display = 'block';
    $.ajax({
      url: '/get_full_mail',
      data: {"mail_id": mail_id},
      method: "POST",
      success: function(data) {
          data = data[0];
          document.getElementById('mail_full_details_header').innerHTML = "<b>SUBJECT : </b>" + data.mail_subject;
          document.getElementById('mail-received-date').innerHTML = "<b>Received Date : </b>" + data.mail_received_date;
          document.getElementById('mail-sender').innerHTML = "<b>SENDER MAIL : </b>" + data.email;
          document.getElementById('mail-sender-name').innerHTML = "<b>SENDER NAME : </b>" + data.first_name + " " + data.last_name;
          document.getElementById('mail-received-body').innerHTML = data.mail_body;
      }
    });
}

function open_action(container_name){
    containers = document.getElementsByClassName('main-container');
    for(let i = 0 ; i < containers.length; i++){
        if(containers[i].id == container_name){
            containers[i].style.display = 'block';
        }else{
            containers[i].style.display = 'none';
        }
    }

}