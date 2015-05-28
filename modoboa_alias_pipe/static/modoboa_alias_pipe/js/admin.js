var AliasPipe = function(options) {
    Listing.call(this, options);
};

AliasPipe.prototype = {
    defaults: {
        deflocation: "list/",
        squery: null
    },

    initialize: function(options) {
        this.options = $.extend({}, this.defaults, options);
        this.options.defcallback = $.proxy(this.list_cb, this);
        Listing.prototype.initialize.call(this, this.options);
        this.listen();
        this.options.navigation_params.push("idtfilter", "grpfilter");
        this.options.eor_message = gettext("No more identity to show");
        this.domain_list = [];
        this.register_tag_handler("idt");
        this.register_tag_handler("grp", this.grp_tag_handler);
    },

    /**
     * Callback used when the initial content of the listing is
     * received.
     *
     * @this AliasPipe
     * @param {Object} data - response of the ajax call (JSON)
     */
    list_cb: function(data) {
        $("#objects_table thead tr").html(data.headers);

        if (data.rows) {
            $("#objects_table tbody").html(data.rows);
        } else {
            $("#objects_table tbody").html("");
        }
        this.update_listing(data);
        if (data.length === 0) {
            this.get_load_page_args();
            this.end_of_list_reached();
        }
        this.init_links(data);
    },

    /**
     * Children must override this method.
     */
    listen: function() {
        $(document).on("click", "a.ajaxnav", $.proxy(this.page_loader, this));
        $(document).on("click", "a.ajaxcall", $.proxy(this.send_call, this));
    },

    /**
     * Load a new page using an AJAX request.
     *
     * @this AliasPipe
     * @param {Object} e - event object
     */
    page_loader: function(e) {
        var $link = get_target(e);
        e.preventDefault();
        if ($link.hasClass("navigation")) {
            $(".sidebar li.active").removeClass("active");
            $link.parent().addClass("active");
        }
        this.navobj.baseurl($link.attr("href")).update();
    },
    add_new_page: function(data, direction) {
        this.init_links(data);
    },

    reload_listing: function(data) {
        this.navobj.update(true);
        if (data) {
            $("body").notify("success", data, 2000);
        }
    },
    send_call: function(evt) {
        var $link = get_target(evt, "a");
        var $this = this;
        var method = $link.attr("data-call_method");

        if (method === undefined) {
            method = "GET";
        }
        evt.preventDefault();
        $.ajax({
            url: $link.attr("href"),
            type: method,
            dataType: "json"
        }).done(function(data) {
            $this.reload_listing(data.respmsg);
        });
    },
    init_links: function(data) {
        $("a[name=delaliaspipe]").confirm({
            question: function() { return this.$element.attr('title'); },
            method: "DELETE",
            success_cb: $.proxy(this.reload_listing, this)
        });
    },
    get_domain_list: function() {
        if (!this.domain_list.length) {
            $.ajax({
                url: this.options.domain_list_url,
                dataType: "json",
                async: false
            }).done($.proxy(function(data) {
                this.domain_list = data;
            }, this));
        }
        return this.domain_list;
    },
    alias_pipe_add: function() {
        $("#id_email").autocompleter({
            from_character: "@",
            choices: this.get_domain_list()
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
                success_cb: $.proxy(this.reload_listing, this)
            });
        }, this));
    },
    alias_pipe_change: function() {
        $("#id_email").autocompleter({
            from_character: "@",
            choices: this.get_domain_list()
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
                success_cb: $.proxy(this.reload_listing, this)
            });
        }, this));
    },
    importform_cb: function() {
        $(".submit").one('click', function(e) {
            e.preventDefault();
            if ($("#id_sourcefile").val() === "") {
                return;
            }
            $("#import_status").css("display", "block");
            $("#import_result").html("").removeClass("alert alert-danger");
            $("#aliaspipeimportform").submit();
        });
    },
    importdone: function(status, msg) {
        $("#import_status").css("display", "none");
        if (status == "ok") {
            $("#modalbox").modal('hide');
            this.reload_listing(msg);
        } else {
            $("#import_result").addClass("alert alert-danger");
            $("#import_result").html(msg);
            this.importform_cb();
        }
    },
};

AliasPipe.prototype = $.extend({}, Listing.prototype, AliasPipe.prototype);

