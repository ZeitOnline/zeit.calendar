
(function() {
    //Declare namespace

    zeit.calendar = {}
}());


(function() {

    zeit.calendar.DND = function(base_url, id) {
        this.base_url = base_url;
        this.contentElement = getElement(id);

        var cal_dnd = this;
        new Droppable(this.contentElement, {
            hoverclass: 'calendar-drop-hover',
            ondrop: function(element, last_active_element, event) {
                cal_dnd.handleDrop(element);
            },
        });
    }

    var DND = zeit.calendar.DND;

    DND.prototype = {

        constructor: DND,

        handleDrop: function(element) {
            var keys = ['form.related.0.', 
                        'form.related.count'];
            var values = [element.uniqueId,  1];

            var qs = queryString(keys, values);

            // redirect
            window.location = this.base_url + '&' + qs
        },

    }

}());


(function() {
    
    zeit.calendar.RessortFilter = function(calendar_url) {
        this.element = $('ressort-filter')
        this.calendar_url = calendar_url;
        connect(this.element, 'onchange', this, 'handleClick');
    }

    var RessortFilter = zeit.calendar.RessortFilter;

    RessortFilter.prototype = {

        handleClick: function(event) {
            var target = event.target();
            if (target.nodeName != 'INPUT') {
                return;
            }
            var class = target.name;
            var active = target.checked;
            this.setClass(class, active);
            this.updateClassOnServer(class, active)
        },

        setClass: function(class, active) {
            var elements = getElementsByTagAndClassName('div', class);
            var func;
            if (active) {
                func = MochiKit.DOM.removeElementClass;
            } else {
                func = MochiKit.DOM.addElementClass;
            }   
            forEach(elements, function(element) {func(element, 'hidden')});
        },

        updateClassOnServer: function(class, active) {
            var view;
            if (active) {
                view = 'show-ressort';
            } else {
                view = 'hide-ressort';
            }
            var url = this.calendar_url + '/@@' + view;
            return doSimpleXMLHttpRequest(url, {ressort: class});
        },

    }

}());
