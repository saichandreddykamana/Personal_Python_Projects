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
      alert(data);
          location.reload();
      }
    });
}
catch(err){
    alert(err)
}
});