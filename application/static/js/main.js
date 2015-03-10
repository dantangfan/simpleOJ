/*! main.js - v0.1.1 - 2014-1-04
* http://admindesigns.com/
* Copyright (c) 2013 Admin Designs;*/

/* Primary theme functions required for
 * most of the sites vital functionality */
var Core = function () {
	
    // Init Eager JS DEMO Loading
    var runPrepJS = function () {

		$(window).load(function() {
			
			// List of all available JS files. We're going to attempt to
			// cache them all after the first page has finished loading.
			// This is for DEMO purposes ONLY
			var scripts = {
				
				// HIGH PRIORITY
				gmap: 			 '/static/vendor/plugins/map/gmaps.min.js',
				jquerymap:		 '/static/vendor/plugins/gmap/jquery.ui.map.js',
				mixitup: 		 '/static/vendor/plugins/mixitup/jquery.mixitup.min.js',
				mpopup: 		 '/static/vendor/plugins/mfpopup/dist/jquery.magnific-popup.min.js',
				chosen:		  	 '/static/vendor/plugins/chosen/chosen.jquery.min.js',
				moment:		 	 '/static/vendor/plugins/daterange/moment.min.js',
				globalize:   	 '/static/vendor/plugins/globalize/globalize.js',
	
				// FORM PICKERS
				cpicker: 	  	 '/static/vendor/plugins/colorpicker/bootstrap-colorpicker.js',
				timepicker:      '/static/vendor/plugins/timepicker/bootstrap-timepicker.min.js',
				datepicker:      '/static/vendor/plugins/datepicker/bootstrap-datepicker.js',
				daterange: 	     '/static/vendor/plugins/daterange/daterangepicker.js',
				
				// FORMS
				validate:		 '/static/vendor/plugins/validate/jquery.validate.js',
				masked: 	 	 '/static/vendor/plugins/jquerymask/jquery.maskedinput.min.js',
				
				// FORMS TOOLS
				holder: 	     '/static/vendor/bootstrap/holder.js',
				tagmanager:      '/static/vendor/plugins/tags/tagmanager.js',
				gritter:         '/static/vendor/plugins/gritter/js/jquery.gritter.min.js',
				ladda:           '/static/vendor/plugins/ladda/ladda.min.js',
				switcher:        '/static/vendor/plugins/formswitch/js/bootstrap-switch.min.js',
				paginator:		 '/static/vendor/bootstrap/paginator/src/bootstrap-paginator.js',
				knob:            '/static/vendor/plugins/jquerydial/jquery.knob.js',
				rangeslider:     '/static/vendor/plugins/rangeslider/jQAllRangeSliders.min.js',
				
				// MED PRIORITY - Large File sizes
				charts:       	 '/static/js/charts.js',
				ckeditorCDN:     'http://cdnjs.cloudflare.com/ajax/libs/ckeditor/4.0.1/ckeditor.js',
				xedit: 			 '/static/vendor/editors/xeditable/js/bootstrap-editable.js',
				summernote:      '/static/vendor/editors/summernote/summernote.js',
				elfinder: 		 '/static/vendor/plugins/elfinder/js/elfinder.min.js',
				countdown:       '/static/vendor/plugins/countdown/jquery.countdown.js',
				jcrop: 			 '/static/vendor/plugins/imagecrop/js/jquery.Jcrop.min.js',
				imagezoom: 		 '/static/vendor/plugins/imagezoom/jquery.elevatezoom.min.js',
				sketchpad:       '/static/vendor/plugins/notepad/wPaint.min.js',
				scrollto: 		 '/static/vendor/plugins/scrollto/jquery.scrollTo-1.4.3.1-min.js',
				fileupload:      '/static/vendor/bootstrap/fileupload/fileupload.js',
				fitvids:		 '/static/vendor/plugins/fitvids/jquery.fitvids.js'	,
				

			};	

			var cacheCheck = function(o) {
				$.each(o, function(i, p) {
					if (localStorage.getItem(i) !== 'cached') {
						$.ajax({
							url: p,
							success: function(data) {
								localStorage.setItem(i, 'cached');
							}				
						});
					}
					else {}
				});
			}
			cacheCheck(scripts);
		});
    }
			
			
    // Init Delayed Animations
    var runDropdowns = function () {
		
		$('.header-btns > div').on('show.bs.dropdown', function() {
				$(this).children('.dropdown-menu').addClass('animated animated-short flipInY');
		});
		$('.header-btns > div').on('hide.bs.dropdown', function() {
				$(this).children('.dropdown-menu').removeClass('animated flipInY');
		});
		
    }
	
    // Init Delayed Animations
    var runAnimations = function () {

	  // if any element has ".animated-delay" we
	  // stop its animation and set a Timeout
	  $('[data-animate]').each(function () {
		  var This = $(this)
		  var delayTime = $(this).data('animate')[0];
		  var delayAnimation = $(this).data('animate')[1];
		  

 	      var delayAnimate = setTimeout(function () {
			  $(This).removeClass('animated-delay').addClass('animated ' + delayAnimation);
		  }, delayTime); 
		  
	  });
    }
	
	
    // Init SideMenu Functions
    var runSideMenu = function () {

        // Collapse Side Menu on Click
        $(".sidebar-toggle").click(toggleSideMenu);
		
        // Adds a single class to body which we use to
        // collapse entire side menu via preset CSS
        function toggleSideMenu() {
            if ($('body').hasClass('sidebar-collapsed')) {
                $('body').removeClass('sidebar-collapsed');
            } 
			else {$('body').addClass('sidebar-collapsed');}
        }

        // If window is under 1200 we remove the sidemenu collapsed class
        // At <1200px CSS media queries will take over and JS will only interfere
        $(window).resize(function () {
            if ($(window).width() < 1200) {
                if ($('body').hasClass('sidebar-collapsed')) {
                    $('body').removeClass('sidebar-collapsed');
                }
            }
        });

        //SideMenu animated accordion toggle
        $('#sidebar-menu .sidebar-nav a.accordion-toggle').click(function (e) {
            e.preventDefault();
			
            var SubMenus = $('#sidebar-menu ul.sub-nav'),
                MenuUrl = $(this).attr('href');
				
            if ($(this).hasClass('collapsed')) {
				
                // To create accordion effect we collapse all open menus
                $('#sidebar-menu .sidebar-nav > li > a.accordion-toggle').addClass('collapsed');
                $(SubMenus).slideUp('fast');
				
                // When effect is complete we remove ".menu-open" class
                $(SubMenus).promise().done(function () {
                    $(SubMenus).removeClass('menu-open');
                });
				
				// We now open the targeted menu item.
                $(this).removeClass('collapsed');
                $(MenuUrl).slideDown('fast', function () {
                    // after the animation we apply the "menu-open" class. 
					// The animation leaves an inline "display:block" style.
					// We remove this as it interferes with media queries 
                    $(MenuUrl).addClass('menu-open').attr('style', '');
                });
            } else {
                $(this).addClass('collapsed');
                $(MenuUrl).slideUp('fast', function () {
                    $(MenuUrl).removeClass('menu-open');
                });
            }
        });
    }

    // Init Form Functions 
    var runTooltips = function () {
        // Init Bootstrap tooltips, if present 
        if ($("[data-toggle=tooltip]").length) {
            $('[data-toggle=tooltip]').tooltip();
        }
    }

    var runPersistCheckbox = function () {
        // Init Bootstrap persistent tooltips. This prevents a
        // popup from closing if a checkbox it contains is clicked
        if ($('.dropdown-menu.checkbox-persist').length) {
            $('.dropdown-menu.checkbox-persist').click(function (event) {
                event.stopPropagation();
            });
        }
    }

    var runFormElements = function () {
        // Init uniform checkboxes, if present
        if ($(".checkbox").length) {
            $(".checkbox").uniform();
        }
        // Init uniform radios, if present
        if ($(".radio").length) {
            $(".radio").uniform();
        }
    }

    // Init Clickable Checklists (header menus/tables)
    var runChecklists = function () {
		
        // Checklist state for table widgets and header menu buttons
        $(".table-checklist tbody tr, .dropdown-checklist .dropdown-items li").click(function () {
            $(this).toggleClass('task-checked');
            if ($(this).hasClass('task-checked')) {
                $(this).find('input.row-checkbox').prop("checked", true);
            } else {
                $(this).find('input.row-checkbox').prop("checked", false);
            }
            $.uniform.update('input.row-checkbox');
        });
		
        // Disable Selection on checklist to prevent excessive text-highlighting
        var disableSelection = function disableSelection() {
            return this.bind(($.support.selectstart ? "selectstart" : "mousedown") + ".ui-disableSelection", function (event) {
                event.preventDefault();
            });
        };
        $(".table-checklist tbody tr").disableSelection();
    }

    // Init Button "active" states
    var runButtonStates = function () {
        // if btn has ".btn-states" class we monitor it for user clicks. On Click we remove
        // the active class from its siblings and give it to the button clicked
        if ($('.btn-states').length) {
            $('.btn-states').click(function () {
                $(this).addClass('active').siblings().removeClass('active');
            });
        }
    }
	
    // Init Header Button Animations
    var runHeader = function () {
        var messageMenu = $('.messages-menu .glyphicon'),
            alertsMenu = $('.alerts-menu .glyphicon'),
            tasksMenu = $('.tasks-menu .glyphicon');
		
		if($('body').hasClass('dashboard')){
			var animate = window.setTimeout(function () {
				$(alertsMenu).animate({color: '#d9534f'}).addClass('animated swing');
				var clear = window.setTimeout(function () {
					$(alertsMenu).animate({color: '#666666'}, 'slow', function() {
						$(this).attr('style','').removeClass('animated bounce');
					});
				}, 1500);
			}, 2300);
			var animate2 = window.setTimeout(function () {
				$(messageMenu).animate({color: '#428bca'}).addClass('animated bounce');
				var clear = window.setTimeout(function () {
					$(messageMenu).animate({color: '#666666'}, 'slow', function() {
						$(this).attr('style','').removeClass('animated bounce');
					});
				}, 1500);
			}, 7300);
		}
    }

    // Init Theme Options/Preview Toolbar  
    var runPreviewPane = function () {

        // toggles skin toolbox
        $('.skin-toolbox-toggle').click(function () {
            if ($(this).hasClass('toolbox-open')) {
                $(this).removeClass('toolbox-open').parent().animate({
                    'right': -182
                }, 'fast');
                localStorage.setItem('toolboxState', 'closed');
            } else {
                $(this).addClass('toolbox-open').parent().animate({
                    'right': -4
                }, 'fast');
                localStorage.setItem('toolboxState', 'open');
            }
        });

        // switch statement for theme layout changes(not customizer)
        $('#skin-toolbox .checkbox, #skin-toolbox .radio').click(function () {
            var id = $(this).attr('id');
            if ($(this).prop('checked')) {
                switch (id) {
                case 'header-option':
                    $('.navbar').addClass('navbar-fixed-top');
                    $('#sidebar-option').attr("disabled", false).parents('label').removeClass('option-disabled');
                    break;
                case 'sidebar-option':
                    $('#sidebar').addClass('affix');
                    if (!$('body').hasClass('boxed-layout')) {
                        $('#breadcrumb-option').attr("disabled", false).parents('label').removeClass('option-disabled');
                    }
                    break;
                case 'breadcrumb-option':
                    $('#topbar').addClass('affix');
                    $('body').addClass('fixed-breadcrumbs');
                    break;
                case 'breadcrumb-hidden':
                    $('body').addClass('hidden-breadcrumbs');
                    break;
                case 'fullwidth-option':
                    $('body').removeClass('boxed-layout boxed-example wide-layout');
                    $('#breadcrumb-option').attr("disabled", false).prop('checked', false).parents('label').removeClass('option-disabled');
                    break;
                case 'boxed-option':
                    $('body').addClass('boxed-layout boxed-example');
                    $('body').removeClass('fixed-breadcrumbs hidden-breadcrumbs hidden-searchbar');
                    $('#topbar').removeClass('affix');
                    $('#breadcrumb-option, #breadcrumb-hidden, #searchbar-hidden').attr('checked', false);
                    $('#breadcrumb-option').attr("disabled", true).parents('label').addClass('option-disabled');
                    break;
                case 'searchbar-hidden':
                    $('body').addClass('hidden-searchbar');
                    break;
                }
            } else {
                switch (id) {
                case 'header-option':
                    $('.navbar').removeClass('navbar-fixed-top');
                    $('body').removeClass('fixed-breadcrumbs');
                    $('#sidebar, #topbar').removeClass('affix');
                    $('#sidebar-option, #breadcrumb-option').attr("disabled", true).prop('checked', this.checked).parents('label').addClass('option-disabled');
                    break;
                case 'sidebar-option':
                    $('#sidebar').removeClass('affix');
                    $('body').removeClass('fixed-breadcrumbs');
                    $('#breadcrumb-option').attr("disabled", true).prop('checked', this.checked).parents('label').addClass('option-disabled');
                    $('#topbar').removeClass('affix');
                    break;
                case 'breadcrumb-option':
                    $('#topbar').removeClass('affix');
                    $('body').removeClass('fixed-breadcrumbs');
                    break;
                case 'breadcrumb-hidden':
                    $('body').removeClass('hidden-breadcrumbs');
                    break;
                case 'searchbar-hidden':
                    $('body').removeClass('hidden-searchbar');
                    break;
                }
            }
            $.uniform.update();
        });
    }
	
	return {
        init: function () {
			runPrepJS();
			runDropdowns();
            runAnimations();
            runSideMenu();
            runFormElements();
            runPersistCheckbox();
            runTooltips();
            runChecklists();
            runButtonStates();
            runHeader();
            runPreviewPane();
        }
	}
	
    
}();