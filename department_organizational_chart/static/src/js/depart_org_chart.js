odoo.define('web.DepartmentOrgChartView', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var concurrency = require('web.concurrency');
var core = require('web.core');
var field_registry = require('web.field_registry');

var QWeb = core.qweb;
var _t = core._t;

var DepartmentOrgChart = AbstractField.extend({

    events: {
        "click .o_department_redirect": "_onDepartRedirect",
        "click .o_department_sub_redirect": "_onDepartSubRedirect",
    },
    /**
     * @constructor
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.dm = new concurrency.DropMisordered();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Get the chart data through a rpc call.
     *
     * @private
     * @param {integer} department_id
     * @returns {Deferred}
     */
    _getOrgData: function (department_id) {
        var self = this;
        return this.dm.add(this._rpc({
            route: '/department/get_org_chart',
            params: {
                department_id: department_id,
            },
        })).then(function (data) {
            self.orgData = data;
        });
    },
    /**
     * @override
     * @private
     */
    _render: function () {
        if (!this.recordData.id) {
            return this.$el.html(QWeb.render("res_depart_org_chart", {
                children: [],
                managers: [],
            }));
        }

        var self = this;
        return this._getOrgData(this.recordData.id).then(function () {
            self.$el.html(QWeb.render("res_depart_org_chart", self.orgData));
            self.$('[data-toggle="popover"]').each(function () {
                $(this).popover({
                    html: true,
                    title: function () {
                        var $title = $(QWeb.render('res_orgchart_depart_popover_title', {
                            department: {
                                name: $(this).data('department-name'),
                                id: $(this).data('department-id'),
                            },
                        }));
                        $title.on('click',
                            '.o_department_redirect', _.bind(self._onDepartRedirect, self));
                        return $title;
                    },
                    container: 'body',
                    placement: 'left',
                    trigger: 'focus',
                    content: function () {
                        var $content = $(QWeb.render('res_orgchart_depart_popover_content', {
                            department: {
                                id: $(this).data('department-id'),
                                name: $(this).data('department-name'),
                                direct_sub_count: parseInt($(this).data('department-dir-subs')),
                                indirect_sub_count: parseInt($(this).data('department-ind-subs')),
                            },
                        }));
                        $content.on('click',
                            '.o_department_sub_redirect', _.bind(self._onDepartSubRedirect, self));
                        return $content;
                    },
                    template: $(QWeb.render('res_orgchart_department_popover', {})),
                });
            });
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Redirect to the partner form view.
     *
     * @private
     * @param {MouseEvent} event
     * @returns {Deferred} action loaded
     */
    _onDepartRedirect: function (event) {
        event.preventDefault();
        var department_id = parseInt($(event.currentTarget).data('department-id'));
        console.log(department_id);
        return this.do_action({
            type: 'ir.actions.act_window',
            view_type: 'form',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'current',
            res_model: 'hr.department',
            res_id: department_id,
        });
    },

    /**
     * Redirect to the sub partner form view.
     *
     * @private
     * @param {MouseEvent} event
     * @returns {Deferred} action loaded
     */
    _onDepartSubRedirect: function (event) {
        event.preventDefault();
        var department_id = parseInt($(event.currentTarget).data('department-id'));
        var department_name = $(event.currentTarget).data('department-name');
        var type = $(event.currentTarget).data('type') || 'direct';
        var domain = [['parent_id', '=', department_id]];
        var name = _.str.sprintf(_t("Direct Subordinates of %s"), department_name);
        if (type === 'total') {
            domain = ['&', ['parent_id', 'child_of', department_id], ['id', '!=', department_id]];
            name = _.str.sprintf(_t("Subordinates of %s"), department_name);
        } else if (type === 'indirect') {
            domain = ['&', '&',
                ['parent_id', 'child_of', department_id],
                ['parent_id', '!=', department_id],
                ['id', '!=', department_id]
            ];
            name = _.str.sprintf(_t("Indirect Subordinates of %s"), department_name);
        }
        if (department_id) {
            return this.do_action({
                name: name,
                type: 'ir.actions.act_window',
                view_mode: 'kanban,list,form',
                views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
                target: 'current',
                res_model: 'hr.department',
                domain: domain,
            });
        }
    },
});

field_registry.add('depart_chart_org', DepartmentOrgChart);

return DepartmentOrgChart;

});
