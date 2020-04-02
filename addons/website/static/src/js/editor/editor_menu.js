odoo.define('website.editor.menu', function (require) {
'use strict';

var Dialog = require('web.Dialog');
var Widget = require('web.Widget');
var core = require('web.core');
var wysiwygLoader = require('web_editor.loader');

var _t = core._t;

var EditorMenu = Widget.extend({
    template: 'website.editorbar',
    xmlDependencies: ['/website/static/src/xml/website.editor.xml'],
    events: {
        'click button[data-action=save]': '_onSaveClick',
        'click button[data-action=cancel]': '_onCancelClick',
    },
    custom_events: {
        request_save: '_onSnippetRequestSave',
        get_clean_html: '_onGetCleanHTML',
    },

    /**
     * @override
     */
    willStart: async function () {
        var self = this;
        this.$el = null; // temporary null to avoid hidden error (@see start)
        await this._super();

        var $wrapwrap = $('#wrapwrap');
        $wrapwrap.removeClass('o_editable'); // clean the dom before edition
        self.editable($wrapwrap).addClass('o_editable');
    },
    /**
     * @override
     */
    start: async function () {
        var self = this;
        this.$el.css({width: '100%'});
        self.wysiwyg = await self._createWysiwyg();
        await this.wysiwyg.attachTo($('#wrapwrap'));
        self.trigger_up('edit_mode');
        self.$el.css({width: ''});
    },
    /**
     * @override
     */
    destroy: function () {
        this.trigger_up('readonly_mode');
        this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Asks the user if they really wants to discard their changes (if any),
     * then simply reloads the page if they want to.
     *
     * @param {boolean} [reload=true]
     *        true if the page has to be reloaded when the user answers yes
     *        (do nothing otherwise but add this to allow class extension)
     * @returns {Deferred}
     */
    cancel: async function (reload) {
        await new Promise( (resolve, reject) => {
            if (!this.wysiwyg.isDirty()) {
                resolve();
            } else {
                var confirm = Dialog.confirm(this, _t("If you discard the current edits, all unsaved changes will be lost. You can cancel to return to edit mode."), {
                    confirm_callback: resolve,
                });
                confirm.on('closed', this, reject);
            }
        });
        this.trigger_up('edition_will_stopped');
    },

    save: async function (reload) {
        this.trigger_up('edition_will_stopped');
        await this.wysiwyg.saveToServer(false);
    },
    /**
     * Returns the editable areas on the page.
     *
     * @param {DOM} $wrapwrap
     * @returns {jQuery}
     */
    editable: function ($wrapwrap) {
        return $wrapwrap.find('[data-oe-model]')
            .not('.o_not_editable')
            .filter(function () {
                var $parent = $(this).closest('.o_editable, .o_not_editable');
                return !$parent.length || $parent.hasClass('o_editable');
            })
            .not('link, script')
            .not('[data-oe-readonly]')
            .not('img[data-oe-field="arch"], br[data-oe-field="arch"], input[data-oe-field="arch"]')
            .not('.oe_snippet_editor')
            .not('hr, br, input, textarea')
            .add('.o_editable');
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _createWysiwyg: async function () {
        var context;
        this.trigger_up('context_get', {
            callback: function (ctx) {
                context = ctx;
            },
        });

        const Wysiwyg = await wysiwygLoader.loadWysiwyg();

        return new Wysiwyg(this, {
            snippets: 'website.snippets',
            recordInfo: {
                context: context,
                data_res_model: 'website',
                data_res_id: context.website_id,
            }, value: $('#wrapwrap')[0].outerHTML,
        });
    },
    /**
     * Reloads the page in non-editable mode, with the right scrolling.
     *
     * @private
     * @returns {Deferred} (never resolved, the page is reloading anyway)
     */
    _reload: function () {
        // should call the reload of the wysiwig
        // this.wysiwyg._reload()
        // return new Promise(function() {});
        $('body').addClass('o_wait_reload');
        this.wysiwyg.destroy();
        this.$el.hide();
        window.location.hash = 'scrollTop=' + window.document.body.scrollTop;
        window.location.reload(true);
        return new Promise(function () {});
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Called when the "Discard" button is clicked -> discards the changes.
     *
     * @private
     */
    _onCancelClick: function () {
        this.cancel(true);
    },
    /**
     * Get the cleaned value of the editable element.
     *
     * @private
     * @param {OdooEvent} ev
     */
    _onGetCleanHTML: function (ev) {
        ev.data.callback(this.wysiwyg.getValue({$layout: ev.data.$layout}));
    },
    /**
     * Snippet (menu_data) can request to save the document to leave the page
     *
     * @private
     * @param {OdooEvent} ev
     * @param {object} ev.data
     * @param {function} ev.data.onSuccess
     * @param {function} ev.data.onFailure
     */
    _onSnippetRequestSave: function (ev) {
        this.save(false).then(ev.data.onSuccess, ev.data.onFailure);
    },
    /**
     * Called when the "Save" button is clicked -> saves the changes.
     *
     * @private
     */
    _onSaveClick: function () {
        this.save();
    },
});

return EditorMenu;
});
