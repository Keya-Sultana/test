/** @odoo-module **/
var listView = require('web.ListView');
var ListRenderer = require('web.ListRenderer');

var ListController = require('web.ListController');
var ListModel = require('web.ListModel');
var view_registry = require('web.view_registry');
const session = require('web.session');
var SampleServer = require('web.SampleServer');

var core = require('web.core');
var QWeb = core.qweb;

let dashboardValues;
SampleServer.mockRegistry.add('indent.indent/retrieve_dashboard', () => {
    return Object.assign({}, dashboardValues);
});

var IndentListDashboardRenderer = ListRenderer.extend({
    events:_.extend({}, ListRenderer.prototype.events, {
        'click .o_dashboard_action': '_onDashboardActionClicked',
    }),
    /**
     * @override
     * @private
     * @returns {Promise}
     */
    _renderView: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            var values = self.state.dashboardValues;
            var indent_dashboard = QWeb.render('stock_indent.IndentDashboard', {
                indentData: values,
            });
            self.$el.prepend(indent_dashboard);
        });
    },

    /**
     * @private
     * @param {MouseEvent}
     */
    _onDashboardActionClicked: function (e) {
        e.preventDefault();
        var $action = $(e.currentTarget);
        this.trigger_up('dashboard_open_action', {
            action_name: "stock_indent.action_stock_indent",
            action_context: $action.attr('context'),
        });
    },
});

var IndentListDashboardModel = ListModel.extend({
    /**
     * @override
     */
    init: function () {
        this.dashboardValues = {};
        this._super.apply(this, arguments);
    },

    /**
     * @override
     */
    __get: function (localID) {
        var result = this._super.apply(this, arguments);
        if (_.isObject(result)) {
            result.dashboardValues = this.dashboardValues[localID];
        }
        return result;
    },
    /**
     * @override
     * @returns {Promise}
     */
    __load: function () {
        return this._loadDashboard(this._super.apply(this, arguments));
    },
    /**
     * @override
     * @returns {Promise}
     */
    __reload: function () {
        return this._loadDashboard(this._super.apply(this, arguments));
    },

    /**
     * @private
     * @param {Promise} super_def a promise that resolves with a dataPoint id
     * @returns {Promise -> string} resolves to the dataPoint id
     */
    _loadDashboard: function (super_def) {
        var self = this;
        var dashboard_def = this._rpc({
            model: 'indent.indent',
            method: 'retrieve_dashboard',
            context: session.user_context,
        });
        return Promise.all([super_def, dashboard_def]).then(function(results) {
            var id = results[0];
            dashboardValues = results[1];
            self.dashboardValues[id] = dashboardValues;
            return id;
        });
    },
});

var IndentListDashboardController = ListController.extend({
    custom_events: _.extend({}, ListController.prototype.custom_events, {
        dashboard_open_action: '_onDashboardOpenAction',
    }),

    /**
     * @private
     * @param {OdooEvent} e
     */
    _onDashboardOpenAction: function (e) {
        return this.do_action(e.data.action_name,
            {additional_context: JSON.parse(e.data.action_context)});
    },
});

var IndentListDashboardView = listView.extend({
    config: _.extend({}, listView.prototype.config, {
        Model: IndentListDashboardModel,
        Renderer: IndentListDashboardRenderer,
        Controller: IndentListDashboardController,
    }),
});

view_registry.add('indent_dashboard_list', IndentListDashboardView);

return {
    IndentListDashboardModel: IndentListDashboardModel,
    IndentListDashboardRenderer: IndentListDashboardRenderer,
    IndentListDashboardController: IndentListDashboardController
};