/*
 feedback.js <http://experiments.hertzen.com/jsfeedback/>
 Copyright (c) 2012 Niklas von Hertzen. All rights reserved.
 http://www.twitter.com/niklasvh

 Released under MIT License
*/
(function( window, document, undefined ) {
/*
  This allows custom messages and languages in the feedback.js library.
  The presidence order for messages is: Custom Message -> i18l -> defaults
  --------------------
  -Change Language: Include or create a language file. See examples at src/i18n/
  -Change Messages: Include or create a custom_message_strings override file

  Example:
    custom_message_strings.header         = "Please, send us your thoughts";
    custom_message_strings.messageSuccess = "Woah, we succeeded!";
*/

// Message getter function
function _(s) {
  return i18n.gettext(s);
}

// Define default messages
var default_message_strings = {
  label: "Feedback",
  header: "Send your Feedback",
  nextLabel: "Continue",
  reviewLabel: "Review",
  sendLabel: "Send",
  closeLabel: "Close",
  messageSuccess: "Your feedback was sent successfully.",
  messageError: "There was an error sending your feedback to our server.",
  formDescription: "Please write your feedback message below, and then click 'Continue' when you're ready",
  highlightDescription: "Click to highlight any parts of the screen related to your message",
  highlight: "Highlight",
  issue: "Issue"
};

var i18n = Object.create({
  'default': default_message_strings,
  'lang': 'default',
  gettext: function(s) {
    var message_strings = this[this.lang] || this[this.lang.substring(0, 2)];
    if (message_strings && message_strings[s]) {
      return message_strings[s];
    } else if (this['default'][s]) {
      return this['default'][s];
    } else {
      return s;
    }
  }
});

i18n.de_DE = {
  label: "Ihre Meinung",
  header: "Senden Sie Ihre Meinung",
  nextLabel: "Weiter",
  reviewLabel: "Überprüfen",
  sendLabel: "Senden",
  closeLabel: "Schliessen",
  messageSuccess: "Ihre Meinung wurde erfolgreich gesendet.",
  messageError: "Fehler beim senden Ihrer Meinung an unser Server.",
  formDescription: "Bitte beschreiben Sie das Problem das bei Ihnen auftritt",
  highlightDescription: "Wichtige Informationen markieren",
  highlight: "Markieren",
  issue: "Problem"
};
i18n.de = i18n.de_DE;

i18n.es_MX = {
  label: "Comentarios",
  header: "Envíe sus comentarios",
  nextLabel: "Continuar",
  reviewLabel: "Revisar",
  sendLabel: "Enviar",
  closeLabel: "Cerrar",
  messageSuccess: "Sus comentarios fueron enviados con éxito.",
  messageError: "Hubo un error al enviar sus comentarios a nuestro servidor.",
  formDescription: "Por favor describa el problema que está experimentando",
  highlightDescription: "Resaltar información importante",
  highlight: "Resaltar",
  issue: "Problema"
};
i18n.es = i18n.es_MX;

i18n.it_IT = {
  label: "Commenta",
  header: "Invia il tuo commento",
  nextLabel: "Continua",
  reviewLabel: "Rivedi",
  sendLabel: "Invia",
  closeLabel: "Chiudi",
  messageSuccess: "Il tuo commento è stato inviato con successo.",
  messageError: "C'è stato un errore nell'invio del tuo commento al nostro server.",
  formDescription: "Per favore descrivi il problema",
  highlightDescription: "Evidenzia le informazioni importanti",
  highlight: "Evidenzia",
  issue: "Problema"
};
i18n.it = i18n.it_IT;

i18n.pt_BR = {
  label: "Comentários",
  header: "Envie seus comentários",
  nextLabel: "Prossegue",
  reviewLabel: "Revisa",
  sendLabel: "Envia",
  closeLabel: "Fecha",
  messageSuccess: "Seus comentários foram enviados com sucesso.",
  messageError: "Houve um erro ao enviar os seus comentários para o nosso servidor.",
  formDescription: "Por favor, descreva o problema que está ocorrendo",
  highlightDescription: "Destaque informação importante",
  highlight: "Destacar",
  issue: "Problema"
};
i18n.pt = i18n.pt_BR;

i18n.ru_RU = {
  label: "Сообщить об ошибке",
  header: "Сообщить об ошибке",
  nextLabel: "Далее",
  reviewLabel: "Далее",
  sendLabel: "Отправить",
  closeLabel: "Закрыть",
  messageSuccess: "Ваше сообщение успешно отправлено.",
  messageError: "Произошла ошибка при отправке сообщения на сервер.",
  formDescription: "Пожалуйста, опишите проблему с которой вы столкнулись",
  highlightDescription: "Выделите важную информацию",
  highlight: "Выделить",
  issue: "Ваше сообщение"
};
i18n.ru = i18n.ru_RU;

if ( window.Feedback !== undefined ) { 
    return; 
}

var loader = function() {
    var div = $('<div />', {'class': 'feedback-loader'});
    [1, 2, 3].forEach(function() { $('<span />').appendTo(div); });
    return div;
},
getBounds = function( el ) {
    return el.getBoundingClientRect();
},
element = function( name, text ) {
    var el = document.createElement( name );
    el.appendChild( document.createTextNode( text ) );
    return el;
},
getLang = function() {
    var lang;
    if (navigator.languages !== undefined) {
        lang = navigator.languages[0];
    } else {
        lang = navigator.language;
    }

    console.log('language = ' + lang);
    if (lang) {
        return lang.replace('-','_');
    }
},
nextButton,
H2C_IGNORE = "data-html2canvas-ignore",
currentPage,
modalBody = $('<div />', {'class': 'feedback-body'});

window.Feedback = function( options ) {

    options = options || {};

    // default properties
    options.url = options.url || "/";
    options.lang = options.lang || "auto";

    if (options.lang === 'auto')
        options.lang = getLang();
    i18n.lang = options.lang;

    if (options.pages === undefined ) {
        options.pages = [
            new window.Feedback.Form(),
            new window.Feedback.Screenshot( options ),
            new window.Feedback.Review()
        ];
    }

    var modal = document.createElement("div"),
    currentPage,
    glass = document.createElement("div"),
    returnMethods = {

        // open send feedback modal window
        open: function() {
            $('header').removeClass('sticky-top');

            options.pages.forEach(function (page) {
                if (page instanceof window.Feedback.Review) return;
                page.render();
            });

            document.body.appendChild(glass);

            // modal close button
            $('#feedback-open').hide();

            // build header element
            modalHeader = $('<div />', {'class': 'feedback-header'});
            modalHeader.append($('<h3 />', {'text': _('header')}));
            modalHeader.append($('<a />', {
                'class': 'feedback-close',
                'click': returnMethods.close,
            }));
            modalHeader.append($('<div />', {'class': 'clear'}));

            currentPage = 0;

            $(modalBody).empty();
            $(modalBody).append($(options.pages[ currentPage++ ].dom));

            // Next button
            nextButton = element( "button", _('nextLabel') );
            nextButton.className =  "feedback-btn";
            nextButton.onclick = function() {
                
                if (currentPage > 0 ) {
                    if ( options.pages[ currentPage - 1 ].end(modal) === false ) {
                        // page failed validation, cancel onclick
                        return;
                    }
                }
                
                $(modalBody).empty();

                var len = options.pages.length;
                if ( currentPage === len ) {
                    returnMethods.send();
                } else {

                    options.pages[ currentPage ].start(modal, nextButton);
                    
                    if ( options.pages[ currentPage ] instanceof window.Feedback.Review ) {
                        // create DOM for review page, based on collected data
                        options.pages[ currentPage ].render( options.pages );
                    }
                    
                    // add page DOM to modal
                    modalBody.append($(options.pages[ currentPage++ ].dom));

                    // if last page, change button label to send
                    if ( currentPage === len ) {
                        nextButton.firstChild.nodeValue = _('sendLabel');
                    }
                    
                    // if next page is review page, change button label
                    if ( options.pages[ currentPage ] instanceof window.Feedback.Review ) {   
                        nextButton.firstChild.nodeValue = _('reviewLabel');
                    }

                }

            };

            var modalFooter = $('<div />', {'class': 'feedback-footer'});
            modalFooter.append($(nextButton));

            $(modal).empty();
            modal.className =  "feedback-modal";
            modal.setAttribute(H2C_IGNORE, true); // don't render in html2canvas
            $(modal).append(modalHeader);
            $(modal).append(modalBody);
            $(modal).append(modalFooter);

            $(document.body).append(modal);
        },


        close: function() {
            $('header').addClass('sticky-top');

            $(modal).remove();
            $(glass).remove();

            if (currentPage > 0 ) {
                options.pages[ currentPage - 1 ].end( modal );
            }
            options.pages.forEach(function(page) {
                page.close();
            });
            $('#feedback-open').show();

            return false;
        },
        send: function() {
            nextButton.disabled = true;

            $(modalBody).empty();
            loader().appendTo($(modalBody));

            var data = [];
            options.pages.forEach(function (page) {
                var pageData = page.data();
                if (pageData) data.push(pageData);
            });

            var adapter = new window.Feedback.XHR(options.url);
            adapter.send(data, function(success) {
                nextButton.disabled = false;
                nextButton.firstChild.nodeValue = _('closeLabel');
                nextButton.onclick = function() {
                    returnMethods.close();
                    return false;  
                };

                var message = _(success ? 'messageSuccess' : 'messageError');
                $(modalBody).empty();
                $(modalBody).text(message);

                options.pages.forEach(function (page) {
                    if (page instanceof window.Feedback.Review) return;
                    delete page._data;
                });
            });
        }
    };

    glass.className = "feedback-glass";
    glass.style.pointerEvents = "none";
    glass.setAttribute(H2C_IGNORE, true);

    options = options || {};

    $(document.body).append(
        $('<button />', {
            'id': 'feedback-open',
            'class': 'feedback-btn feedback-bottom-right',
            'text': _('label'),
            'attr': {H2C_IGNORE: true},
            'click': returnMethods.open
        })
    );
    
    return returnMethods;
};

window.Feedback.Page = function() {};
window.Feedback.Page.prototype = {
    render: function(dom) { this.dom = dom; },
    start: function() {},
    close: function() {},
    data: function() { return false; },
    review: function() { return null; },
    end: function() { return true; }

};
window.Feedback.Send = function() {};
window.Feedback.Send.prototype = {
    send: function() {}
};

window.Feedback.Form = function(elements) {
    this.elements = elements || [{
        type: 'textarea',
        name: 'issue',
        label: _('formDescription')
    }];
    this.dom = document.createElement('div');
};
window.Feedback.Form.prototype = new window.Feedback.Page();
window.Feedback.Form.prototype.render = function() {
    var $this = this;
    $(this.dom).empty();
    this.elements.forEach(function(item) {
        switch (item.type) {
            case 'textarea':
                $this.dom.appendChild(element('label', item.label));
                $this.dom.appendChild(item.element = document.createElement('textarea'));
                break;
        }
    });
    return this;
};
window.Feedback.Form.prototype.data = function() {
    
    if (this._data) return this._data;
    
    var data = {};
    this.elements.forEach(function(item) {
        data[item.name] = item.element.value;
    });
    data.url = window.location.href;
    data.timeOpened = new Date();
    data.timezone = (new Date()).getTimezoneOffset()/60;
    data.pageon = window.location.pathname;
    data.referrer = document.referrer;
    data.previousSites = history.length;
    data.browserName = navigator.appName;
    data.browserEngine = navigator.product;
    data.browserVersion1a = navigator.appVersion;
    data.browserVersion1b = navigator.userAgent;
    data.browserLanguage = navigator.language;
    data.browserOnline = navigator.onLine;
    data.browserPlatform = navigator.platform;
    data.javaEnabled = navigator.javaEnabled();
    data.dataCookiesEnabled = navigator.cookieEnabled;
    data.dataCookies1 = document.cookie;
    data.dataCookies2 = decodeURIComponent(document.cookie.split(";"));
    data.dataStorage = localStorage;
    data.sizeScreenW = screen.width;
    data.sizeScreenH = screen.height;
    data.sizeDocW = document.width;
    data.sizeDocH = document.height;
    data.sizeInW = innerWidth;
    data.sizeInH = innerHeight;
    data.sizeAvailW = screen.availWidth;
    data.sizeAvailH = screen.availHeight;
    data.scrColorDepth = screen.colorDepth;
    data.scrPixelDepth = screen.pixelDepth;

    return this._data = data;
};
window.Feedback.Form.prototype.review = function(dom) {
    this.elements.forEach(function(item) {
        if (item.element.value.length > 0) {
            dom.appendChild(element('label', 'Feedback:'));
            dom.appendChild(document.createTextNode(' '));
            dom.appendChild(document.createTextNode(item.element.value ));
            dom.appendChild(document.createElement('hr'));
        }
    })
    return dom;
};

window.Feedback.Review = function() {
    this.dom = document.createElement("div");
    this.dom.className = "feedback-review";
};

window.Feedback.Review.prototype = new window.Feedback.Page();
window.Feedback.Review.prototype.render = function( pages ) {
    $(this.dom).empty();
    var $this = this;
    pages.forEach(function (page) {
        page.review($this.dom);
    });
    return this;
};




window.Feedback.Screenshot = function( options ) {
    this.options = options || {};
    this.options.highlightClass = this.options.highlightClass || 'feedback-highlighted';
};

window.Feedback.Screenshot.prototype = new window.Feedback.Page();
window.Feedback.Screenshot.prototype.end = function(modal) {
    $(modal).removeClass('feedback-animate-toside');
    $(document.body).off('mousemove', this.mouseMoveEvent);
    $(document.body).off('click', this.mouseClickEvent);
    $(this.h2cCanvas).remove();
};

window.Feedback.Screenshot.prototype.close = function(){
    $(this.highlightBox).remove();
    $(this.highlightClose).remove();
    $('.' + this.options.highlightClass).remove();
};

window.Feedback.Screenshot.prototype.start = function(modal, nextButton) {
    var $this = this;
    var $arguments = arguments;

    if (!this.h2cDone) {
        if (nextButton.disabled !== true) {
            loader().appendTo($(this.dom));
        }
        nextButton.disabled = true;
        window.setTimeout(function() { $this.start.apply($this, $arguments) }, 500);
        return;
    }

    $(this.dom).empty();
    nextButton.disabled = false;

    var feedbackHighlightElement = "feedback-highlight-element",
    dataExclude = "data-exclude";

    // delegate mouse move event for body
    this.mouseMoveEvent = function( e ) {

        if (e.target === document.body || e.target === highlightClose || $(modal).has(e.target).length) {
            clearBox();
            return;
        } else if ($(e.target).hasClass($this.options.highlightClass)) {
            bounds = getBounds(e.target);
            $(highlightClose).css({
                'left': (window.pageXOffset + bounds.left + bounds.width) + 'px',
                'top': (window.pageYOffset + bounds.top) + 'px'
            }).show();

            removeElement = e.target;
            clearBox();
            return;
        } else {
            $(highlightClose).hide();
        }

        if (e.target !== previousElement ) {
            previousElement = e.target;

            var bounds = getBounds(e.target);

            var item = highlightBox;
            item.width = bounds.width;
            item.height = bounds.height;
            ctx.drawImage($this.h2cCanvas, window.pageXOffset + bounds.left, window.pageYOffset + bounds.top, bounds.width, bounds.height, 0, 0, bounds.width, bounds.height );

            // we are only targetting IE>=9, so window.pageYOffset works fine
            item.setAttribute(dataExclude, false);
            item.style.left = window.pageXOffset + bounds.left + "px";
            item.style.top = window.pageYOffset + bounds.top + "px";
            item.style.width = bounds.width + "px";
            item.style.height = bounds.height + "px";
            removeElement = item;
        }
    };

    // delegate event for body click
    this.mouseClickEvent = function( e ){
        e.preventDefault();
        if (highlightBox.getAttribute(dataExclude) === "false") {
            highlightBox.className += " " + $this.options.highlightClass;
            highlightBox.className = highlightBox.className.replace(/feedback\-highlight\-element/g,"");
            $this.highlightBox = highlightBox = document.createElement('canvas');

            ctx = highlightBox.getContext("2d");

            highlightBox.className += " " + feedbackHighlightElement;

            document.body.appendChild( highlightBox );
            clearBox();
            previousElement = undefined;

            bounds = getBounds(e.target);
            $(highlightClose).css({
                'left': (window.pageXOffset + bounds.left + bounds.width) + 'px',
                'top': (window.pageYOffset + bounds.top) + 'px'
            }).show();
        }
    };

    this.highlightClose = element("div", "×");
    this.highlightBox = document.createElement( "canvas" );
    var highlightClose = this.highlightClose,
    highlightBox = this.highlightBox,
    removeElement,
    ctx = highlightBox.getContext("2d"),
    clearBox = function() {
        clearBoxEl(highlightBox);
    },
    clearBoxEl = function( el ) {
        el.style.left =  "-5px";
        el.style.top =  "-5px";
        el.style.width = "0px";
        el.style.height = "0px";
        el.setAttribute(dataExclude, true);
    },
    previousElement;

    $(modal).addClass('feedback-animate-toside');

    highlightClose.id = "feedback-highlight-close";
    highlightClose.addEventListener("click", function() {
        $(removeElement).remove();
        $(this).hide();
    }, false);
    document.body.appendChild(highlightClose);

    this.h2cCanvas.className = 'feedback-canvas';
    document.body.appendChild( this.h2cCanvas);

    this.dom.appendChild(element("p", _('highlightDescription')));

    this.highlightBox.className += " " + feedbackHighlightElement;
    document.body.appendChild( this.highlightBox );

    // bind mouse delegate events
    $(document.body).on('mousemove', this.mouseMoveEvent);
    $(document.body).on('click', this.mouseClickEvent);
};

window.Feedback.Screenshot.prototype.render = function() {
    this.dom = document.createElement("div");
    this.h2cDone = false;

    // execute the html2canvas script
    var $this = this, options = this.options;
    $.getScript(options.h2cPath, function() {
        window.html2canvas(document.body, options).then(function(canvas) {
            $this.h2cCanvas = canvas;
            $this.h2cDone = true;
        }).catch(function(e) {
            $this.h2cDone = true;
            console.log("Error in html2canvas: " + e.message);
        });
    });
    return this;
};

window.Feedback.Screenshot.prototype.data = function() {
    if (!this.h2cCanvas) return;

    var ctx = this.h2cCanvas.getContext("2d"),
        canvasCopy,
        copyCtx,
        radius = 5;
        ctx.fillStyle = "#000";

    // draw highlights
    var items = Array.prototype.slice.call( document.getElementsByClassName('feedback-highlighted'), 0);
    if (items.length > 0 ) {
        canvasCopy = document.createElement( "canvas" );
        copyCtx = canvasCopy.getContext('2d');
        canvasCopy.width = this.h2cCanvas.width;
        canvasCopy.height = this.h2cCanvas.height;
        copyCtx.drawImage(this.h2cCanvas, 0, 0);

        ctx.fillStyle = "#777";
        ctx.globalAlpha = 0.5;
        ctx.fillRect( 0, 0, this.h2cCanvas.width, this.h2cCanvas.height );
        ctx.beginPath();

        items.forEach(function(item) {
            var x = parseInt(item.style.left, 10),
                y = parseInt(item.style.top, 10),
                width = parseInt(item.style.width, 10),
                height = parseInt(item.style.height, 10);

            ctx.moveTo(x + radius, y);
            ctx.lineTo(x + width - radius, y);
            ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
            ctx.lineTo(x + width, y + height - radius);
            ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
            ctx.lineTo(x + radius, y + height);
            ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
            ctx.lineTo(x, y + radius);
            ctx.quadraticCurveTo(x, y, x + radius, y);
        });
        ctx.closePath();
        ctx.clip();
        ctx.globalAlpha = 1;
        ctx.drawImage(canvasCopy, 0,0);
    }
        
    try { return this.h2cCanvas.toDataURL(); } catch (e) {}
};


window.Feedback.Screenshot.prototype.review = function(dom) {
    var data = this.data();
    if (data) {
        var img = new Image();
        img.src = data;
        dom.appendChild(img);
    }
};

window.Feedback.XHR = function(url) { this.url = url; };
window.Feedback.XHR.prototype = new window.Feedback.Send();
window.Feedback.XHR.prototype.send = function(data, callback) {
    $.post({
        url: this.url,
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function() { callback(true) },
        error: function() { callback(false) }
    });
};
})(window, document);
