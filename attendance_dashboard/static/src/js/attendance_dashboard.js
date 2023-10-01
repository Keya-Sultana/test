odoo.define('attendance.dashboard', function (require) {
  "use strict";

  /**
   * This file defines the Purchase Dashboard view (alongside its renderer, model
   * and controller). This Dashboard is added to the top of list and kanban Purchase
   * views, it extends both views with essentially the same code except for
   * _onDashboardActionClicked function so we can apply filters without changing our
   * current view.
   */
  var core = require('web.core');
  var ListController = require('web.ListController');
  var ListModel = require('web.ListModel');
  var ListRenderer = require('web.ListRenderer');
  var ListView = require('web.ListView');
  var SampleServer = require('web.SampleServer');
  var view_registry = require('web.view_registry');
  const session = require('web.session');
  var rpc = require('web.rpc');

  var QWeb = core.qweb;

// Add mock of method 'retrieve_dashboard' in SampleServer, so that we can have
// the sample data in empty purchase kanban and list view
  let dashboardValues;
  SampleServer.mockRegistry.add('hr.attendance/retrieve_dashboard', () => {
    return Object.assign({}, dashboardValues);
  });

//--------------------------------------------------------------------------
// List View
//--------------------------------------------------------------------------

  var AttendanceListDashboardRenderer = ListRenderer.extend({
    events: _.extend({}, ListRenderer.prototype.events, {
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
        var attendance_dashboard = QWeb.render('attendance_dashboard.AttendanceDashboard', {
          values: values,
        });
        self.$el.prepend(attendance_dashboard);
      });
    },

    /**
     * @private
     * @param {MouseEvent}
     */
    _onDashboardActionClicked: function (e) {
      e.preventDefault();
      var $action = $(e.currentTarget);

      return rpc.query({
        model: 'hr.attendance',
        method: 'sync_manually',
        args: [""]
      })

      // this.trigger_up('dashboard_open_action', {
      //   action_name: "hr.attendance.sync_manually",
      // });
    },
  });

  var AttendanceListDashboardModel = ListModel.extend({
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
        model: 'hr.attendance',
        method: 'retrieve_dashboard',
        context: session.user_context,
      });
      return Promise.all([super_def, dashboard_def]).then(function (results) {
        var id = results[0];
        dashboardValues = results[1];
        self.dashboardValues[id] = dashboardValues;
        return id;
      });
    },
  });

  var AttendanceListDashboardController = ListController.extend({
    custom_events: _.extend({}, ListController.prototype.custom_events, {
      dashboard_open_action: '_onDashboardOpenAction',
    }),

    /**
     * @private
     * @param {OdooEvent} e
     */
    _onDashboardOpenAction: function (e) {
      return this.do_action(e.data.action_name,
        { additional_context: JSON.parse(e.data.action_context) });
    },
  });

  var AttendanceListDashboardView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
      Model: AttendanceListDashboardModel,
      Renderer: AttendanceListDashboardRenderer,
      Controller: AttendanceListDashboardController,
    }),
  });


  view_registry.add('attendance_list_dashboard', AttendanceListDashboardView);

  return {
    AttendanceListDashboardModel: AttendanceListDashboardModel,
    AttendanceListDashboardRenderer: AttendanceListDashboardRenderer,
    AttendanceListDashboardController: AttendanceListDashboardController
  };

});
