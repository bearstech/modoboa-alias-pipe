function alias_pipe_add() {
  $("#id_email").autocompleter({
    from_character: "@",
    choices: admin.get_domain_list()
  });

  $("#original_recipients").dynamic_input({
    input_added: function($row) {
      $row.find("label").html("");
    },
    input_removed: function($input) {
      $input.parents(".form-group").remove();
      return true;
    }
  });

  $(".submit").on('click', $.proxy(function(e) {
    simple_ajax_form_post(e, {
      formid: "aliaspipeform",
      reload_on_success: false,
      success_cb: function() {
        admin.reload_listing();
      }
    });
  }, this));
};
