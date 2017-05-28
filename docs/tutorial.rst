**************
NDlib Tutorial
**************


NDlib is built upon networkx and is designed to configure, simulate and
visualize diffusion experiments. In order to install the latest version
of the library (with visualization facilities) use

::

    pip install ndlib

Let's start importing the required libraries

.. code:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.epidemics.SIRModel as sir

NDlib identifies fours stages of simulation definition - Network
Definition (generation/loading - networkx) - Model Selection - Model
Configuration - Step by step simulation

.. code:: python

    # Network Definition
    g = nx.erdos_renyi_graph(1000, 0.1)
    
    # Model Selection
    model = sir.SIRModel(g)
    
    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter('beta', 0.001)
    config.add_model_parameter('gamma', 0.01)
    config.add_model_parameter("percentage_infected", 0.05)
    model.set_initial_status(config)
    
    # Simulation
    iterations = model.iteration_bunch(200)

At the end of the simulation the diffusion trend can be visualized as
follows

.. code:: python

    from bokeh.io import output_notebook, show
    from ndlib.viz.bokeh.DiffusionTrend import DiffusionTrend
    
    output_notebook()
    
    viz = DiffusionTrend(model, iterations)
    p = viz.plot(width=400, height=400)
    show(p)



.. raw:: html

    
        <div class="bk-root">
            <a href="http://bokeh.pydata.org" target="_blank" class="bk-logo bk-logo-small bk-logo-notebook"></a>
            <span id="7002605c-3c80-4319-ad61-806ff313b039">Loading BokehJS ...</span>
        </div>





.. raw:: html

    
    
        <div class="bk-root">
            <div class="bk-plotdiv" id="088669d5-6a8b-4cdd-96e8-d8f94df0811a"></div>
        </div>
    <script type="text/javascript">
      
      (function(global) {
        function now() {
          return new Date();
        }
      
        var force = false;
      
        if (typeof (window._bokeh_onload_callbacks) === "undefined" || force === true) {
          window._bokeh_onload_callbacks = [];
          window._bokeh_is_loading = undefined;
        }
      
      
        
        if (typeof (window._bokeh_timeout) === "undefined" || force === true) {
          window._bokeh_timeout = Date.now() + 0;
          window._bokeh_failed_load = false;
        }
      
        var NB_LOAD_WARNING = {'data': {'text/html':
           "<div style='background-color: #fdd'>\n"+
           "<p>\n"+
           "BokehJS does not appear to have successfully loaded. If loading BokehJS from CDN, this \n"+
           "may be due to a slow or bad network connection. Possible fixes:\n"+
           "</p>\n"+
           "<ul>\n"+
           "<li>re-rerun `output_notebook()` to attempt to load from CDN again, or</li>\n"+
           "<li>use INLINE resources instead, as so:</li>\n"+
           "</ul>\n"+
           "<code>\n"+
           "from bokeh.resources import INLINE\n"+
           "output_notebook(resources=INLINE)\n"+
           "</code>\n"+
           "</div>"}};
      
        function display_loaded() {
          if (window.Bokeh !== undefined) {
            document.getElementById("088669d5-6a8b-4cdd-96e8-d8f94df0811a").textContent = "BokehJS successfully loaded.";
          } else if (Date.now() < window._bokeh_timeout) {
            setTimeout(display_loaded, 100)
          }
        }
      
        function run_callbacks() {
          window._bokeh_onload_callbacks.forEach(function(callback) { callback() });
          delete window._bokeh_onload_callbacks
          console.info("Bokeh: all callbacks have finished");
        }
      
        function load_libs(js_urls, callback) {
          window._bokeh_onload_callbacks.push(callback);
          if (window._bokeh_is_loading > 0) {
            console.log("Bokeh: BokehJS is being loaded, scheduling callback at", now());
            return null;
          }
          if (js_urls == null || js_urls.length === 0) {
            run_callbacks();
            return null;
          }
          console.log("Bokeh: BokehJS not loaded, scheduling load and callback at", now());
          window._bokeh_is_loading = js_urls.length;
          for (var i = 0; i < js_urls.length; i++) {
            var url = js_urls[i];
            var s = document.createElement('script');
            s.src = url;
            s.async = false;
            s.onreadystatechange = s.onload = function() {
              window._bokeh_is_loading--;
              if (window._bokeh_is_loading === 0) {
                console.log("Bokeh: all BokehJS libraries loaded");
                run_callbacks()
              }
            };
            s.onerror = function() {
              console.warn("failed to load library " + url);
            };
            console.log("Bokeh: injecting script tag for BokehJS library: ", url);
            document.getElementsByTagName("head")[0].appendChild(s);
          }
        };var element = document.getElementById("088669d5-6a8b-4cdd-96e8-d8f94df0811a");
        if (element == null) {
          console.log("Bokeh: ERROR: autoload.js configured with elementid '088669d5-6a8b-4cdd-96e8-d8f94df0811a' but no matching script tag was found. ")
          return false;
        }
      
        var js_urls = [];
      
        var inline_js = [
          function(Bokeh) {
            (function() {
              var fn = function() {
                var docs_json = {"86cb041d-ca70-444b-9ae1-962ace066cc8":{"roots":{"references":[{"attributes":{"align":"center","plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"text":"percentage infected: 0.05, beta: 0.001, gamma: 0.01"},"id":"cb87025e-3f3b-48a4-a1c0-aec9c8af3205","type":"Title"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"1ef72fa5-2382-4fc5-a70b-1c801cb7076d","type":"HelpTool"},{"attributes":{"below":[{"id":"39ccff6f-cdcf-4ddb-a0b5-fa52ad5425f5","type":"LinearAxis"},{"id":"cb87025e-3f3b-48a4-a1c0-aec9c8af3205","type":"Title"}],"left":[{"id":"7b1dace5-aaf9-462f-88b8-7f8feecbfb2d","type":"LinearAxis"}],"plot_height":400,"plot_width":400,"renderers":[{"id":"39ccff6f-cdcf-4ddb-a0b5-fa52ad5425f5","type":"LinearAxis"},{"id":"951cabcb-14a5-4601-9795-5f0f440a1e1f","type":"Grid"},{"id":"7b1dace5-aaf9-462f-88b8-7f8feecbfb2d","type":"LinearAxis"},{"id":"ce449e57-2c0e-4bcf-b58d-674abde975a9","type":"Grid"},{"id":"2aa729d3-0267-4b47-9c86-ae38a1666c11","type":"BoxAnnotation"},{"id":"4b1db386-6e2c-4f05-b333-c37d2ee5a870","type":"Legend"},{"id":"ab15b2c1-2506-4559-b296-0444a1a4df10","type":"GlyphRenderer"},{"id":"2f291fbf-aa58-403b-9656-c032207caf75","type":"GlyphRenderer"},{"id":"c9426e74-3afd-45c1-8aa8-e385731b8da2","type":"GlyphRenderer"},{"id":"cb87025e-3f3b-48a4-a1c0-aec9c8af3205","type":"Title"}],"title":{"id":"783bec4f-5692-4e65-b5ad-d43a008640de","type":"Title"},"tool_events":{"id":"a4c444ea-afe2-42ff-934e-8221368e5123","type":"ToolEvents"},"toolbar":{"id":"fff415bf-dbc0-441a-a759-dc72f26c8b4f","type":"Toolbar"},"x_range":{"id":"b035140b-eb4e-4e76-bb04-021785201d9e","type":"DataRange1d"},"y_range":{"id":"676e91bc-7212-4e2c-b653-193e08d8f7ca","type":"DataRange1d"}},"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},{"attributes":{},"id":"2fc18aae-753e-4f4b-b4db-1fda66da8ffa","type":"BasicTickFormatter"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"70c0ee7e-500b-49a2-af4b-44a42dd82cda","type":"SaveTool"},{"attributes":{"axis_label":"#Nodes","formatter":{"id":"2fc18aae-753e-4f4b-b4db-1fda66da8ffa","type":"BasicTickFormatter"},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"ticker":{"id":"32184b0f-dd31-489e-af88-98ba58a2b8ac","type":"BasicTicker"}},"id":"7b1dace5-aaf9-462f-88b8-7f8feecbfb2d","type":"LinearAxis"},{"attributes":{"items":[{"id":"909ac954-0acd-40b7-8797-da82af402b4a","type":"LegendItem"},{"id":"996c6dba-dc48-489d-8445-a83ce75ea7b5","type":"LegendItem"},{"id":"bd422dde-b71e-4c36-b31d-80b27c2abe2c","type":"LegendItem"}],"orientation":"horizontal","plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"4b1db386-6e2c-4f05-b333-c37d2ee5a870","type":"Legend"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"2aa729d3-0267-4b47-9c86-ae38a1666c11","type":"BoxAnnotation"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"f1345f17-8a99-4ab9-a43a-ec2dea23342b","type":"Line"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"c6e3a379-610d-45d6-96b2-f732a2e94e6e","type":"WheelZoomTool"},{"attributes":{"plot":null,"text":"SIR - Diffusion Trend"},"id":"783bec4f-5692-4e65-b5ad-d43a008640de","type":"Title"},{"attributes":{"data_source":{"id":"6d2ade8c-5a1f-4d07-a7d6-0a58bd25f973","type":"ColumnDataSource"},"glyph":{"id":"485837af-4003-481d-9e3b-22c770c076ed","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"de0f30d8-f393-47ea-95bd-2a8828bd3f36","type":"Line"},"selection_glyph":null},"id":"2f291fbf-aa58-403b-9656-c032207caf75","type":"GlyphRenderer"},{"attributes":{"data_source":{"id":"c78ad910-d6a7-40ca-a9a7-44b214e1be06","type":"ColumnDataSource"},"glyph":{"id":"040b41a0-d154-45fa-9230-a174ebf98b72","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"f1345f17-8a99-4ab9-a43a-ec2dea23342b","type":"Line"},"selection_glyph":null},"id":"c9426e74-3afd-45c1-8aa8-e385731b8da2","type":"GlyphRenderer"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[0,2,2,2,4,4,7,7,7,9,10,11,11,11,12,13,15,17,19,22,24,25,28,30,31,34,35,40,46,51,54,61,67,71,79,82,86,93,101,105,117,121,130,136,143,148,150,156,163,172,180,185,189,198,207,212,215,225,237,244,248,251,262,265,269,273,280,286,298,308,315,326,335,341,343,349,354,358,367,372,375,383,389,401,408,418,421,426,434,443,453,456,461,467,471,472,487,491,497,500,509,512,518,524,526,528,532,535,539,544,546,552,556,561,563,564,569,574,580,582,582,583,588,595,599,605,610,618,622,624,625,634,636,640,645,647,652,655,659,661,667,673,677,683,686,689,693,698,702,704,707,710,714,715,719,719,720,723,727,728,733,737,741,744,746,748,753,755,757,759,759,763,764,765,768,770,771,772,774,775,781,784,785,786,788,791,797,799,802,806,808,813,817,820,823,827,828,828,830,831]}},"id":"c78ad910-d6a7-40ca-a9a7-44b214e1be06","type":"ColumnDataSource"},{"attributes":{"callback":null},"id":"676e91bc-7212-4e2c-b653-193e08d8f7ca","type":"DataRange1d"},{"attributes":{"label":{"value":"Susceptible"},"renderers":[{"id":"ab15b2c1-2506-4559-b296-0444a1a4df10","type":"GlyphRenderer"}]},"id":"909ac954-0acd-40b7-8797-da82af402b4a","type":"LegendItem"},{"attributes":{"line_color":{"value":"#aec7e8"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"485837af-4003-481d-9e3b-22c770c076ed","type":"Line"},{"attributes":{"grid_line_alpha":{"value":0.5},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"ticker":{"id":"8654eb6a-1e02-4506-b86a-bcd84e471080","type":"BasicTicker"}},"id":"951cabcb-14a5-4601-9795-5f0f440a1e1f","type":"Grid"},{"attributes":{},"id":"32184b0f-dd31-489e-af88-98ba58a2b8ac","type":"BasicTicker"},{"attributes":{"overlay":{"id":"2aa729d3-0267-4b47-9c86-ae38a1666c11","type":"BoxAnnotation"},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"1af75cd2-afd0-4bb2-ac55-afc6a5c2ca33","type":"BoxZoomTool"},{"attributes":{},"id":"098eff25-f41e-40b4-9aca-f1206151a05b","type":"BasicTickFormatter"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"214731b7-c8fa-4871-8d0f-2c4e985f0b87","type":"Line"},{"attributes":{"label":{"value":"Removed"},"renderers":[{"id":"c9426e74-3afd-45c1-8aa8-e385731b8da2","type":"GlyphRenderer"}]},"id":"bd422dde-b71e-4c36-b31d-80b27c2abe2c","type":"LegendItem"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[950,943,936,927,921,911,904,897,888,879,870,862,851,840,828,816,804,789,772,754,741,726,707,684,663,636,606,580,565,536,510,484,466,446,419,397,373,343,328,311,292,269,252,245,227,208,194,187,173,161,147,142,139,131,118,105,99,91,84,82,79,75,70,66,65,62,59,47,44,41,37,35,34,32,31,30,29,28,26,25,23,20,19,19,17,17,17,16,15,15,13,12,12,11,11,10,10,9,9,9,9,9,9,9,8,8,7,7,7,7,7,6,6,6,6,6,6,6,6,6,5,5,4,4,4,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]}},"id":"5acb4cd5-c097-479c-bdc3-4d7fce2974ec","type":"ColumnDataSource"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[50,55,62,71,75,85,89,96,105,112,120,127,138,149,160,171,181,194,209,224,235,249,265,286,306,330,359,380,389,413,436,455,467,483,502,521,541,564,571,584,591,610,618,619,630,644,656,657,664,667,673,673,672,671,675,683,686,684,679,674,673,674,668,669,666,665,661,667,658,651,648,639,631,627,626,621,617,614,607,603,602,597,592,580,575,565,562,558,551,542,534,532,527,522,518,518,503,500,494,491,482,479,473,467,466,464,461,458,454,449,447,442,438,433,431,430,425,420,414,412,413,412,408,401,397,392,387,379,376,374,373,364,362,358,353,351,346,343,339,337,331,325,321,315,312,309,305,300,296,294,291,288,284,283,279,279,278,275,271,270,265,261,257,254,252,250,245,243,241,239,239,235,234,233,230,228,227,226,224,223,217,214,213,212,210,207,201,199,196,192,190,185,181,178,175,171,170,170,168,167]}},"id":"6d2ade8c-5a1f-4d07-a7d6-0a58bd25f973","type":"ColumnDataSource"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"48376b2c-7869-4a12-a480-c577074066c2","type":"PanTool"},{"attributes":{},"id":"8654eb6a-1e02-4506-b86a-bcd84e471080","type":"BasicTicker"},{"attributes":{"label":{"value":"Infected"},"renderers":[{"id":"2f291fbf-aa58-403b-9656-c032207caf75","type":"GlyphRenderer"}]},"id":"996c6dba-dc48-489d-8445-a83ce75ea7b5","type":"LegendItem"},{"attributes":{"callback":null},"id":"b035140b-eb4e-4e76-bb04-021785201d9e","type":"DataRange1d"},{"attributes":{"dimension":1,"grid_line_alpha":{"value":0.5},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"ticker":{"id":"32184b0f-dd31-489e-af88-98ba58a2b8ac","type":"BasicTicker"}},"id":"ce449e57-2c0e-4bcf-b58d-674abde975a9","type":"Grid"},{"attributes":{},"id":"a4c444ea-afe2-42ff-934e-8221368e5123","type":"ToolEvents"},{"attributes":{"active_drag":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"48376b2c-7869-4a12-a480-c577074066c2","type":"PanTool"},{"id":"c6e3a379-610d-45d6-96b2-f732a2e94e6e","type":"WheelZoomTool"},{"id":"1af75cd2-afd0-4bb2-ac55-afc6a5c2ca33","type":"BoxZoomTool"},{"id":"70c0ee7e-500b-49a2-af4b-44a42dd82cda","type":"SaveTool"},{"id":"53498048-937f-435c-9e55-c246830e877b","type":"ResetTool"},{"id":"1ef72fa5-2382-4fc5-a70b-1c801cb7076d","type":"HelpTool"}]},"id":"fff415bf-dbc0-441a-a759-dc72f26c8b4f","type":"Toolbar"},{"attributes":{"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"2573568d-59d5-4dc4-8400-58d6572df9ee","type":"Line"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"53498048-937f-435c-9e55-c246830e877b","type":"ResetTool"},{"attributes":{"line_color":{"value":"#ff7f0e"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"040b41a0-d154-45fa-9230-a174ebf98b72","type":"Line"},{"attributes":{"data_source":{"id":"5acb4cd5-c097-479c-bdc3-4d7fce2974ec","type":"ColumnDataSource"},"glyph":{"id":"2573568d-59d5-4dc4-8400-58d6572df9ee","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"214731b7-c8fa-4871-8d0f-2c4e985f0b87","type":"Line"},"selection_glyph":null},"id":"ab15b2c1-2506-4559-b296-0444a1a4df10","type":"GlyphRenderer"},{"attributes":{"axis_label":"Iterations","formatter":{"id":"098eff25-f41e-40b4-9aca-f1206151a05b","type":"BasicTickFormatter"},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"ticker":{"id":"8654eb6a-1e02-4506-b86a-bcd84e471080","type":"BasicTicker"}},"id":"39ccff6f-cdcf-4ddb-a0b5-fa52ad5425f5","type":"LinearAxis"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"de0f30d8-f393-47ea-95bd-2a8828bd3f36","type":"Line"}],"root_ids":["9391ef7c-0136-4870-a9cc-cac314cebfe9"]},"title":"Bokeh Application","version":"0.12.4"}};
                var render_items = [{"docid":"86cb041d-ca70-444b-9ae1-962ace066cc8","elementid":"088669d5-6a8b-4cdd-96e8-d8f94df0811a","modelid":"9391ef7c-0136-4870-a9cc-cac314cebfe9"}];
                
                Bokeh.embed.embed_items(docs_json, render_items);
              };
              if (document.readyState != "loading") fn();
              else document.addEventListener("DOMContentLoaded", fn);
            })();
          },
          function(Bokeh) {
          }
        ];
      
        function run_inline_js() {
          
          if ((window.Bokeh !== undefined) || (force === true)) {
            for (var i = 0; i < inline_js.length; i++) {
              inline_js[i](window.Bokeh);
            }if (force === true) {
              display_loaded();
            }} else if (Date.now() < window._bokeh_timeout) {
            setTimeout(run_inline_js, 100);
          } else if (!window._bokeh_failed_load) {
            console.log("Bokeh: BokehJS failed to load within specified timeout.");
            window._bokeh_failed_load = true;
          } else if (force !== true) {
            var cell = $(document.getElementById("088669d5-6a8b-4cdd-96e8-d8f94df0811a")).parents('.cell').data().cell;
            cell.output_area.append_execute_result(NB_LOAD_WARNING)
          }
      
        }
      
        if (window._bokeh_is_loading === 0) {
          console.log("Bokeh: BokehJS loaded, going straight to plotting");
          run_inline_js();
        } else {
          load_libs(js_urls, function() {
            console.log("Bokeh: BokehJS plotting callback run at", now());
            run_inline_js();
          });
        }
      }(this));
    </script>


Furthermore, a prevalence plot is available. The prevalence plot
captures the variation (delta) of nodes in each status in consecutive
iterations.

.. code:: python

    from ndlib.viz.bokeh.DiffusionPrevalence import DiffusionPrevalence
    
    viz2 = DiffusionPrevalence(model, iterations)
    p2 = viz2.plot(width=400, height=400)
    
    show(p2)



.. raw:: html

    
    
        <div class="bk-root">
            <div class="bk-plotdiv" id="6ea75708-072e-4a1d-965b-f29353141c37"></div>
        </div>
    <script type="text/javascript">
      
      (function(global) {
        function now() {
          return new Date();
        }
      
        var force = false;
      
        if (typeof (window._bokeh_onload_callbacks) === "undefined" || force === true) {
          window._bokeh_onload_callbacks = [];
          window._bokeh_is_loading = undefined;
        }
      
      
        
        if (typeof (window._bokeh_timeout) === "undefined" || force === true) {
          window._bokeh_timeout = Date.now() + 0;
          window._bokeh_failed_load = false;
        }
      
        var NB_LOAD_WARNING = {'data': {'text/html':
           "<div style='background-color: #fdd'>\n"+
           "<p>\n"+
           "BokehJS does not appear to have successfully loaded. If loading BokehJS from CDN, this \n"+
           "may be due to a slow or bad network connection. Possible fixes:\n"+
           "</p>\n"+
           "<ul>\n"+
           "<li>re-rerun `output_notebook()` to attempt to load from CDN again, or</li>\n"+
           "<li>use INLINE resources instead, as so:</li>\n"+
           "</ul>\n"+
           "<code>\n"+
           "from bokeh.resources import INLINE\n"+
           "output_notebook(resources=INLINE)\n"+
           "</code>\n"+
           "</div>"}};
      
        function display_loaded() {
          if (window.Bokeh !== undefined) {
            document.getElementById("6ea75708-072e-4a1d-965b-f29353141c37").textContent = "BokehJS successfully loaded.";
          } else if (Date.now() < window._bokeh_timeout) {
            setTimeout(display_loaded, 100)
          }
        }
      
        function run_callbacks() {
          window._bokeh_onload_callbacks.forEach(function(callback) { callback() });
          delete window._bokeh_onload_callbacks
          console.info("Bokeh: all callbacks have finished");
        }
      
        function load_libs(js_urls, callback) {
          window._bokeh_onload_callbacks.push(callback);
          if (window._bokeh_is_loading > 0) {
            console.log("Bokeh: BokehJS is being loaded, scheduling callback at", now());
            return null;
          }
          if (js_urls == null || js_urls.length === 0) {
            run_callbacks();
            return null;
          }
          console.log("Bokeh: BokehJS not loaded, scheduling load and callback at", now());
          window._bokeh_is_loading = js_urls.length;
          for (var i = 0; i < js_urls.length; i++) {
            var url = js_urls[i];
            var s = document.createElement('script');
            s.src = url;
            s.async = false;
            s.onreadystatechange = s.onload = function() {
              window._bokeh_is_loading--;
              if (window._bokeh_is_loading === 0) {
                console.log("Bokeh: all BokehJS libraries loaded");
                run_callbacks()
              }
            };
            s.onerror = function() {
              console.warn("failed to load library " + url);
            };
            console.log("Bokeh: injecting script tag for BokehJS library: ", url);
            document.getElementsByTagName("head")[0].appendChild(s);
          }
        };var element = document.getElementById("6ea75708-072e-4a1d-965b-f29353141c37");
        if (element == null) {
          console.log("Bokeh: ERROR: autoload.js configured with elementid '6ea75708-072e-4a1d-965b-f29353141c37' but no matching script tag was found. ")
          return false;
        }
      
        var js_urls = [];
      
        var inline_js = [
          function(Bokeh) {
            (function() {
              var fn = function() {
                var docs_json = {"271fe117-7fea-46cd-ad41-1bfe031a0e7e":{"roots":{"references":[{"attributes":{"label":{"value":"Removed"},"renderers":[{"id":"b2e45137-0318-4568-935c-507665224e53","type":"GlyphRenderer"}]},"id":"b15f80d0-9a95-4220-9fb0-8c4a1580dfb4","type":"LegendItem"},{"attributes":{"plot":null,"text":"SIR - Prevalence"},"id":"33aa9349-96bc-49ba-a6ec-745f6116860d","type":"Title"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"a5b7eddd-bbe5-4157-93b1-c453c43d6fe3","type":"Line"},{"attributes":{"items":[{"id":"10a521c3-1f69-432c-b3d2-d7d13ca60fab","type":"LegendItem"},{"id":"6317df25-82a4-4993-810d-5d125249037e","type":"LegendItem"},{"id":"b15f80d0-9a95-4220-9fb0-8c4a1580dfb4","type":"LegendItem"}],"orientation":"horizontal","plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"bfefdfeb-8826-48b1-9a88-7dbd98f6de82","type":"Legend"},{"attributes":{"align":"center","plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"},"text":"percentage infected: 0.05, beta: 0.001, gamma: 0.01"},"id":"50441167-2012-44bb-9920-8c01326d546a","type":"Title"},{"attributes":{"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"c6994d32-768a-4694-b002-5b091ad62bd4","type":"WheelZoomTool"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"5fc4ca7a-5eee-4433-9e92-a856648ee14a","type":"Line"},{"attributes":{"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"faf78620-c3dd-414a-b76b-ce9a46cba6eb","type":"HelpTool"},{"attributes":{"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"22d6c60f-32b1-4e56-8e29-af02ddf563c8","type":"PanTool"},{"attributes":{"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"c4930aa1-9bb3-4a16-b89e-7a1ba5df51ba","type":"ResetTool"},{"attributes":{},"id":"4d5ad420-3d61-416d-9d1e-91cd959bebbf","type":"ToolEvents"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198],"y":[6,6,7,5,10,5,5,8,7,7,7,11,10,10,9,5,13,12,13,10,15,17,17,18,17,23,19,6,22,17,15,10,13,15,18,18,18,5,10,5,13,5,-1,7,11,8,-2,6,0,4,-1,-1,-1,0,7,0,-1,-6,-5,-2,0,-5,-2,-2,-1,-4,4,-9,-5,-4,-9,-8,-4,-1,-5,-3,-3,-7,-5,-1,-6,-6,-12,-6,-10,-3,-5,-7,-9,-8,-2,-4,-6,-4,-1,-14,-3,-5,-3,-9,-3,-6,-6,-2,-2,-3,-3,-4,-5,-2,-5,-4,-4,-2,-1,-5,-5,-6,-2,0,-1,-5,-7,-4,-5,-5,-8,-4,-2,-1,-8,-2,-4,-5,-2,-4,-3,-3,-2,-6,-6,-4,-6,-3,-3,-3,-5,-3,-2,-3,-3,-4,-1,-4,0,-1,-2,-4,-1,-5,-4,-3,-3,-2,-2,-5,-2,-2,-2,0,-4,-1,-1,-3,-2,-1,-1,-1,-1,-5,-3,-1,-1,-2,-3,-6,-2,-3,-4,-2,-5,-4,-2,-3,-4,-1,0,-2,-1]}},"id":"6139dedd-1e8a-4f6c-b4d2-607e4f1d9af7","type":"ColumnDataSource"},{"attributes":{"grid_line_alpha":{"value":0.5},"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"},"ticker":{"id":"0630c29f-b2da-4de4-b653-19a543d21893","type":"BasicTicker"}},"id":"c61dddae-a1ce-49e4-b219-37460871295a","type":"Grid"},{"attributes":{"callback":null},"id":"85b05a36-5d74-47b4-971b-9605a2df9a7f","type":"DataRange1d"},{"attributes":{},"id":"9056b210-7c99-4fea-9629-54a0f9d79a33","type":"BasicTickFormatter"},{"attributes":{},"id":"2283b2bd-c777-411a-9aaa-525e09bbc60e","type":"BasicTicker"},{"attributes":{"line_color":{"value":"#aec7e8"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"91975a66-63d3-4725-afa5-830b12350508","type":"Line"},{"attributes":{"data_source":{"id":"2987d600-505e-4122-a21b-45c37371387e","type":"ColumnDataSource"},"glyph":{"id":"6d0e21da-9942-42a2-a49c-89ac1ee187ac","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"04fddfc5-afdf-464e-8768-4d0b3ce5f876","type":"Line"},"selection_glyph":null},"id":"fe6fd0de-7efd-4b79-ab5c-1e90566cfe6a","type":"GlyphRenderer"},{"attributes":{"callback":null},"id":"0086e3a7-c3c5-4db1-99e0-8fee7b1f2eaf","type":"DataRange1d"},{"attributes":{"line_color":{"value":"#ff7f0e"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"54251b77-5d2c-4d87-8d0b-430044aec53b","type":"Line"},{"attributes":{"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"f35fb413-3a07-4fb8-9c10-2367c2709b16","type":"SaveTool"},{"attributes":{"overlay":{"id":"33084629-22b5-4627-af22-7ee4d15df4ab","type":"BoxAnnotation"},"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"b8f252e3-1b81-4110-9364-c8743b91ee83","type":"BoxZoomTool"},{"attributes":{"data_source":{"id":"6139dedd-1e8a-4f6c-b4d2-607e4f1d9af7","type":"ColumnDataSource"},"glyph":{"id":"91975a66-63d3-4725-afa5-830b12350508","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"5fc4ca7a-5eee-4433-9e92-a856648ee14a","type":"Line"},"selection_glyph":null},"id":"9a7f6e31-fdbe-42bb-a2f0-eee8815c6f2f","type":"GlyphRenderer"},{"attributes":{"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"6d0e21da-9942-42a2-a49c-89ac1ee187ac","type":"Line"},{"attributes":{"axis_label":"Iterations","formatter":{"id":"9056b210-7c99-4fea-9629-54a0f9d79a33","type":"BasicTickFormatter"},"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"},"ticker":{"id":"0630c29f-b2da-4de4-b653-19a543d21893","type":"BasicTicker"}},"id":"15653d31-9be8-45f5-b943-a4b5cb0f49d2","type":"LinearAxis"},{"attributes":{"active_drag":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"22d6c60f-32b1-4e56-8e29-af02ddf563c8","type":"PanTool"},{"id":"c6994d32-768a-4694-b002-5b091ad62bd4","type":"WheelZoomTool"},{"id":"b8f252e3-1b81-4110-9364-c8743b91ee83","type":"BoxZoomTool"},{"id":"f35fb413-3a07-4fb8-9c10-2367c2709b16","type":"SaveTool"},{"id":"c4930aa1-9bb3-4a16-b89e-7a1ba5df51ba","type":"ResetTool"},{"id":"faf78620-c3dd-414a-b76b-ce9a46cba6eb","type":"HelpTool"}]},"id":"ed8a0a5d-21c7-45bb-803d-1baa1407b58f","type":"Toolbar"},{"attributes":{"data_source":{"id":"6517ac4d-6086-415b-96c5-65c3f26d9295","type":"ColumnDataSource"},"glyph":{"id":"54251b77-5d2c-4d87-8d0b-430044aec53b","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"a5b7eddd-bbe5-4157-93b1-c453c43d6fe3","type":"Line"},"selection_glyph":null},"id":"b2e45137-0318-4568-935c-507665224e53","type":"GlyphRenderer"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"33084629-22b5-4627-af22-7ee4d15df4ab","type":"BoxAnnotation"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198],"y":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}},"id":"2987d600-505e-4122-a21b-45c37371387e","type":"ColumnDataSource"},{"attributes":{"dimension":1,"grid_line_alpha":{"value":0.5},"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"},"ticker":{"id":"2283b2bd-c777-411a-9aaa-525e09bbc60e","type":"BasicTicker"}},"id":"4ba26872-123e-4db2-9f54-8733982dce41","type":"Grid"},{"attributes":{},"id":"0630c29f-b2da-4de4-b653-19a543d21893","type":"BasicTicker"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198],"y":[-6,-6,-7,-5,-10,-5,-5,-8,-7,-7,-7,-11,-10,-10,-9,-5,-13,-12,-13,-10,-15,-17,-17,-18,-17,-23,-19,-6,-22,-17,-15,-10,-13,-15,-18,-18,-18,-5,-10,-5,-13,-5,1,-7,-11,-8,2,-6,0,-4,1,1,1,0,-7,0,1,6,5,2,0,5,2,2,1,4,-4,9,5,4,9,8,4,1,5,3,3,7,5,1,6,6,12,6,10,3,5,7,9,8,2,4,6,4,1,14,3,5,3,9,3,6,6,2,2,3,3,4,5,2,5,4,4,2,1,5,5,6,2,0,1,5,7,4,5,5,8,4,2,1,8,2,4,5,2,4,3,3,2,6,6,4,6,3,3,3,5,3,2,3,3,4,1,4,0,1,2,4,1,5,4,3,3,2,2,5,2,2,2,0,4,1,1,3,2,1,1,1,1,5,3,1,1,2,3,6,2,3,4,2,5,4,2,3,4,1,0,2,1]}},"id":"6517ac4d-6086-415b-96c5-65c3f26d9295","type":"ColumnDataSource"},{"attributes":{"below":[{"id":"15653d31-9be8-45f5-b943-a4b5cb0f49d2","type":"LinearAxis"},{"id":"50441167-2012-44bb-9920-8c01326d546a","type":"Title"}],"left":[{"id":"dd134c98-c27b-4ebd-b7ab-2747cf3fd7bd","type":"LinearAxis"}],"plot_height":400,"plot_width":400,"renderers":[{"id":"15653d31-9be8-45f5-b943-a4b5cb0f49d2","type":"LinearAxis"},{"id":"c61dddae-a1ce-49e4-b219-37460871295a","type":"Grid"},{"id":"dd134c98-c27b-4ebd-b7ab-2747cf3fd7bd","type":"LinearAxis"},{"id":"4ba26872-123e-4db2-9f54-8733982dce41","type":"Grid"},{"id":"33084629-22b5-4627-af22-7ee4d15df4ab","type":"BoxAnnotation"},{"id":"bfefdfeb-8826-48b1-9a88-7dbd98f6de82","type":"Legend"},{"id":"fe6fd0de-7efd-4b79-ab5c-1e90566cfe6a","type":"GlyphRenderer"},{"id":"9a7f6e31-fdbe-42bb-a2f0-eee8815c6f2f","type":"GlyphRenderer"},{"id":"b2e45137-0318-4568-935c-507665224e53","type":"GlyphRenderer"},{"id":"50441167-2012-44bb-9920-8c01326d546a","type":"Title"}],"title":{"id":"33aa9349-96bc-49ba-a6ec-745f6116860d","type":"Title"},"tool_events":{"id":"4d5ad420-3d61-416d-9d1e-91cd959bebbf","type":"ToolEvents"},"toolbar":{"id":"ed8a0a5d-21c7-45bb-803d-1baa1407b58f","type":"Toolbar"},"x_range":{"id":"85b05a36-5d74-47b4-971b-9605a2df9a7f","type":"DataRange1d"},"y_range":{"id":"0086e3a7-c3c5-4db1-99e0-8fee7b1f2eaf","type":"DataRange1d"}},"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"},{"attributes":{"axis_label":"#Delta Nodes","formatter":{"id":"a4c4e9c9-adf9-43fe-bc53-f0b02588f29e","type":"BasicTickFormatter"},"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"},"ticker":{"id":"2283b2bd-c777-411a-9aaa-525e09bbc60e","type":"BasicTicker"}},"id":"dd134c98-c27b-4ebd-b7ab-2747cf3fd7bd","type":"LinearAxis"},{"attributes":{},"id":"a4c4e9c9-adf9-43fe-bc53-f0b02588f29e","type":"BasicTickFormatter"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"04fddfc5-afdf-464e-8768-4d0b3ce5f876","type":"Line"},{"attributes":{"label":{"value":"Infected"},"renderers":[{"id":"9a7f6e31-fdbe-42bb-a2f0-eee8815c6f2f","type":"GlyphRenderer"}]},"id":"6317df25-82a4-4993-810d-5d125249037e","type":"LegendItem"},{"attributes":{"label":{"value":"Susceptible"},"renderers":[{"id":"fe6fd0de-7efd-4b79-ab5c-1e90566cfe6a","type":"GlyphRenderer"}]},"id":"10a521c3-1f69-432c-b3d2-d7d13ca60fab","type":"LegendItem"}],"root_ids":["2fdf096c-378c-4b73-8ecc-dcba5bc1ca02"]},"title":"Bokeh Application","version":"0.12.4"}};
                var render_items = [{"docid":"271fe117-7fea-46cd-ad41-1bfe031a0e7e","elementid":"6ea75708-072e-4a1d-965b-f29353141c37","modelid":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02"}];
                
                Bokeh.embed.embed_items(docs_json, render_items);
              };
              if (document.readyState != "loading") fn();
              else document.addEventListener("DOMContentLoaded", fn);
            })();
          },
          function(Bokeh) {
          }
        ];
      
        function run_inline_js() {
          
          if ((window.Bokeh !== undefined) || (force === true)) {
            for (var i = 0; i < inline_js.length; i++) {
              inline_js[i](window.Bokeh);
            }if (force === true) {
              display_loaded();
            }} else if (Date.now() < window._bokeh_timeout) {
            setTimeout(run_inline_js, 100);
          } else if (!window._bokeh_failed_load) {
            console.log("Bokeh: BokehJS failed to load within specified timeout.");
            window._bokeh_failed_load = true;
          } else if (force !== true) {
            var cell = $(document.getElementById("6ea75708-072e-4a1d-965b-f29353141c37")).parents('.cell').data().cell;
            cell.output_area.append_execute_result(NB_LOAD_WARNING)
          }
      
        }
      
        if (window._bokeh_is_loading === 0) {
          console.log("Bokeh: BokehJS loaded, going straight to plotting");
          run_inline_js();
        } else {
          load_libs(js_urls, function() {
            console.log("Bokeh: BokehJS plotting callback run at", now());
            run_inline_js();
          });
        }
      }(this));
    </script>


Multiple plots can be combined in a multiplot to provide a complete
description of the diffusive process

.. code:: python

    from ndlib.viz.bokeh.MultiPlot import MultiPlot
    
    vm = MultiPlot()
    
    vm.add_plot(p)
    vm.add_plot(p2)
    m = vm.plot()
    show(m)



.. raw:: html

    
    
        <div class="bk-root">
            <div class="bk-plotdiv" id="c6021a60-5b3a-4383-8ab9-4f07cf593a91"></div>
        </div>
    <script type="text/javascript">
      
      (function(global) {
        function now() {
          return new Date();
        }
      
        var force = false;
      
        if (typeof (window._bokeh_onload_callbacks) === "undefined" || force === true) {
          window._bokeh_onload_callbacks = [];
          window._bokeh_is_loading = undefined;
        }
      
      
        
        if (typeof (window._bokeh_timeout) === "undefined" || force === true) {
          window._bokeh_timeout = Date.now() + 0;
          window._bokeh_failed_load = false;
        }
      
        var NB_LOAD_WARNING = {'data': {'text/html':
           "<div style='background-color: #fdd'>\n"+
           "<p>\n"+
           "BokehJS does not appear to have successfully loaded. If loading BokehJS from CDN, this \n"+
           "may be due to a slow or bad network connection. Possible fixes:\n"+
           "</p>\n"+
           "<ul>\n"+
           "<li>re-rerun `output_notebook()` to attempt to load from CDN again, or</li>\n"+
           "<li>use INLINE resources instead, as so:</li>\n"+
           "</ul>\n"+
           "<code>\n"+
           "from bokeh.resources import INLINE\n"+
           "output_notebook(resources=INLINE)\n"+
           "</code>\n"+
           "</div>"}};
      
        function display_loaded() {
          if (window.Bokeh !== undefined) {
            document.getElementById("c6021a60-5b3a-4383-8ab9-4f07cf593a91").textContent = "BokehJS successfully loaded.";
          } else if (Date.now() < window._bokeh_timeout) {
            setTimeout(display_loaded, 100)
          }
        }
      
        function run_callbacks() {
          window._bokeh_onload_callbacks.forEach(function(callback) { callback() });
          delete window._bokeh_onload_callbacks
          console.info("Bokeh: all callbacks have finished");
        }
      
        function load_libs(js_urls, callback) {
          window._bokeh_onload_callbacks.push(callback);
          if (window._bokeh_is_loading > 0) {
            console.log("Bokeh: BokehJS is being loaded, scheduling callback at", now());
            return null;
          }
          if (js_urls == null || js_urls.length === 0) {
            run_callbacks();
            return null;
          }
          console.log("Bokeh: BokehJS not loaded, scheduling load and callback at", now());
          window._bokeh_is_loading = js_urls.length;
          for (var i = 0; i < js_urls.length; i++) {
            var url = js_urls[i];
            var s = document.createElement('script');
            s.src = url;
            s.async = false;
            s.onreadystatechange = s.onload = function() {
              window._bokeh_is_loading--;
              if (window._bokeh_is_loading === 0) {
                console.log("Bokeh: all BokehJS libraries loaded");
                run_callbacks()
              }
            };
            s.onerror = function() {
              console.warn("failed to load library " + url);
            };
            console.log("Bokeh: injecting script tag for BokehJS library: ", url);
            document.getElementsByTagName("head")[0].appendChild(s);
          }
        };var element = document.getElementById("c6021a60-5b3a-4383-8ab9-4f07cf593a91");
        if (element == null) {
          console.log("Bokeh: ERROR: autoload.js configured with elementid 'c6021a60-5b3a-4383-8ab9-4f07cf593a91' but no matching script tag was found. ")
          return false;
        }
      
        var js_urls = [];
      
        var inline_js = [
          function(Bokeh) {
            (function() {
              var fn = function() {
                var docs_json = {"053faff6-6e76-4cc8-b281-fc58aac2842a":{"roots":{"references":[{"attributes":{"align":"center","plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"text":"percentage infected: 0.05, beta: 0.001, gamma: 0.01"},"id":"cb87025e-3f3b-48a4-a1c0-aec9c8af3205","type":"Title"},{"attributes":{"label":{"value":"Removed"},"renderers":[{"id":"b2e45137-0318-4568-935c-507665224e53","type":"GlyphRenderer"}]},"id":"b15f80d0-9a95-4220-9fb0-8c4a1580dfb4","type":"LegendItem"},{"attributes":{"plot":null,"text":"SIR - Prevalence"},"id":"33aa9349-96bc-49ba-a6ec-745f6116860d","type":"Title"},{"attributes":{"below":[{"id":"39ccff6f-cdcf-4ddb-a0b5-fa52ad5425f5","type":"LinearAxis"},{"id":"cb87025e-3f3b-48a4-a1c0-aec9c8af3205","type":"Title"}],"left":[{"id":"7b1dace5-aaf9-462f-88b8-7f8feecbfb2d","type":"LinearAxis"}],"plot_height":400,"plot_width":400,"renderers":[{"id":"39ccff6f-cdcf-4ddb-a0b5-fa52ad5425f5","type":"LinearAxis"},{"id":"951cabcb-14a5-4601-9795-5f0f440a1e1f","type":"Grid"},{"id":"7b1dace5-aaf9-462f-88b8-7f8feecbfb2d","type":"LinearAxis"},{"id":"ce449e57-2c0e-4bcf-b58d-674abde975a9","type":"Grid"},{"id":"2aa729d3-0267-4b47-9c86-ae38a1666c11","type":"BoxAnnotation"},{"id":"4b1db386-6e2c-4f05-b333-c37d2ee5a870","type":"Legend"},{"id":"ab15b2c1-2506-4559-b296-0444a1a4df10","type":"GlyphRenderer"},{"id":"2f291fbf-aa58-403b-9656-c032207caf75","type":"GlyphRenderer"},{"id":"c9426e74-3afd-45c1-8aa8-e385731b8da2","type":"GlyphRenderer"},{"id":"cb87025e-3f3b-48a4-a1c0-aec9c8af3205","type":"Title"}],"title":{"id":"783bec4f-5692-4e65-b5ad-d43a008640de","type":"Title"},"tool_events":{"id":"a4c444ea-afe2-42ff-934e-8221368e5123","type":"ToolEvents"},"toolbar":{"id":"fff415bf-dbc0-441a-a759-dc72f26c8b4f","type":"Toolbar"},"toolbar_location":null,"x_range":{"id":"b035140b-eb4e-4e76-bb04-021785201d9e","type":"DataRange1d"},"y_range":{"id":"676e91bc-7212-4e2c-b653-193e08d8f7ca","type":"DataRange1d"}},"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},{"attributes":{},"id":"2fc18aae-753e-4f4b-b4db-1fda66da8ffa","type":"BasicTickFormatter"},{"attributes":{"callback":null},"id":"0086e3a7-c3c5-4db1-99e0-8fee7b1f2eaf","type":"DataRange1d"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"70c0ee7e-500b-49a2-af4b-44a42dd82cda","type":"SaveTool"},{"attributes":{"align":"center","plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"},"text":"percentage infected: 0.05, beta: 0.001, gamma: 0.01"},"id":"50441167-2012-44bb-9920-8c01326d546a","type":"Title"},{"attributes":{"axis_label":"#Nodes","formatter":{"id":"2fc18aae-753e-4f4b-b4db-1fda66da8ffa","type":"BasicTickFormatter"},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"ticker":{"id":"32184b0f-dd31-489e-af88-98ba58a2b8ac","type":"BasicTicker"}},"id":"7b1dace5-aaf9-462f-88b8-7f8feecbfb2d","type":"LinearAxis"},{"attributes":{"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"c6994d32-768a-4694-b002-5b091ad62bd4","type":"WheelZoomTool"},{"attributes":{"items":[{"id":"909ac954-0acd-40b7-8797-da82af402b4a","type":"LegendItem"},{"id":"996c6dba-dc48-489d-8445-a83ce75ea7b5","type":"LegendItem"},{"id":"bd422dde-b71e-4c36-b31d-80b27c2abe2c","type":"LegendItem"}],"orientation":"horizontal","plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"4b1db386-6e2c-4f05-b333-c37d2ee5a870","type":"Legend"},{"attributes":{"label":{"value":"Susceptible"},"renderers":[{"id":"ab15b2c1-2506-4559-b296-0444a1a4df10","type":"GlyphRenderer"}]},"id":"909ac954-0acd-40b7-8797-da82af402b4a","type":"LegendItem"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"33084629-22b5-4627-af22-7ee4d15df4ab","type":"BoxAnnotation"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"2aa729d3-0267-4b47-9c86-ae38a1666c11","type":"BoxAnnotation"},{"attributes":{"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"22d6c60f-32b1-4e56-8e29-af02ddf563c8","type":"PanTool"},{"attributes":{"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"faf78620-c3dd-414a-b76b-ce9a46cba6eb","type":"HelpTool"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"f1345f17-8a99-4ab9-a43a-ec2dea23342b","type":"Line"},{"attributes":{"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"c4930aa1-9bb3-4a16-b89e-7a1ba5df51ba","type":"ResetTool"},{"attributes":{},"id":"4d5ad420-3d61-416d-9d1e-91cd959bebbf","type":"ToolEvents"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198],"y":[6,6,7,5,10,5,5,8,7,7,7,11,10,10,9,5,13,12,13,10,15,17,17,18,17,23,19,6,22,17,15,10,13,15,18,18,18,5,10,5,13,5,-1,7,11,8,-2,6,0,4,-1,-1,-1,0,7,0,-1,-6,-5,-2,0,-5,-2,-2,-1,-4,4,-9,-5,-4,-9,-8,-4,-1,-5,-3,-3,-7,-5,-1,-6,-6,-12,-6,-10,-3,-5,-7,-9,-8,-2,-4,-6,-4,-1,-14,-3,-5,-3,-9,-3,-6,-6,-2,-2,-3,-3,-4,-5,-2,-5,-4,-4,-2,-1,-5,-5,-6,-2,0,-1,-5,-7,-4,-5,-5,-8,-4,-2,-1,-8,-2,-4,-5,-2,-4,-3,-3,-2,-6,-6,-4,-6,-3,-3,-3,-5,-3,-2,-3,-3,-4,-1,-4,0,-1,-2,-4,-1,-5,-4,-3,-3,-2,-2,-5,-2,-2,-2,0,-4,-1,-1,-3,-2,-1,-1,-1,-1,-5,-3,-1,-1,-2,-3,-6,-2,-3,-4,-2,-5,-4,-2,-3,-4,-1,0,-2,-1]}},"id":"6139dedd-1e8a-4f6c-b4d2-607e4f1d9af7","type":"ColumnDataSource"},{"attributes":{"grid_line_alpha":{"value":0.5},"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"},"ticker":{"id":"0630c29f-b2da-4de4-b653-19a543d21893","type":"BasicTicker"}},"id":"c61dddae-a1ce-49e4-b219-37460871295a","type":"Grid"},{"attributes":{"plot":null,"text":"SIR - Diffusion Trend"},"id":"783bec4f-5692-4e65-b5ad-d43a008640de","type":"Title"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198],"y":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}},"id":"2987d600-505e-4122-a21b-45c37371387e","type":"ColumnDataSource"},{"attributes":{"data_source":{"id":"6d2ade8c-5a1f-4d07-a7d6-0a58bd25f973","type":"ColumnDataSource"},"glyph":{"id":"485837af-4003-481d-9e3b-22c770c076ed","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"de0f30d8-f393-47ea-95bd-2a8828bd3f36","type":"Line"},"selection_glyph":null},"id":"2f291fbf-aa58-403b-9656-c032207caf75","type":"GlyphRenderer"},{"attributes":{"data_source":{"id":"c78ad910-d6a7-40ca-a9a7-44b214e1be06","type":"ColumnDataSource"},"glyph":{"id":"040b41a0-d154-45fa-9230-a174ebf98b72","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"f1345f17-8a99-4ab9-a43a-ec2dea23342b","type":"Line"},"selection_glyph":null},"id":"c9426e74-3afd-45c1-8aa8-e385731b8da2","type":"GlyphRenderer"},{"attributes":{},"id":"9056b210-7c99-4fea-9629-54a0f9d79a33","type":"BasicTickFormatter"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"a5b7eddd-bbe5-4157-93b1-c453c43d6fe3","type":"Line"},{"attributes":{"callback":null},"id":"676e91bc-7212-4e2c-b653-193e08d8f7ca","type":"DataRange1d"},{"attributes":{"line_color":{"value":"#ff7f0e"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"54251b77-5d2c-4d87-8d0b-430044aec53b","type":"Line"},{"attributes":{"line_color":{"value":"#aec7e8"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"91975a66-63d3-4725-afa5-830b12350508","type":"Line"},{"attributes":{"line_color":{"value":"#aec7e8"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"485837af-4003-481d-9e3b-22c770c076ed","type":"Line"},{"attributes":{"data_source":{"id":"2987d600-505e-4122-a21b-45c37371387e","type":"ColumnDataSource"},"glyph":{"id":"6d0e21da-9942-42a2-a49c-89ac1ee187ac","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"04fddfc5-afdf-464e-8768-4d0b3ce5f876","type":"Line"},"selection_glyph":null},"id":"fe6fd0de-7efd-4b79-ab5c-1e90566cfe6a","type":"GlyphRenderer"},{"attributes":{"children":[{"id":"52049298-0a93-4f82-9c9c-3d23300a4dd9","type":"ToolbarBox"},{"id":"784f5132-6f87-4a69-85c7-8d4eb9ac6d48","type":"Column"}]},"id":"0fd11d07-cc0c-405b-961b-eb00748838c0","type":"Column"},{"attributes":{},"id":"2283b2bd-c777-411a-9aaa-525e09bbc60e","type":"BasicTicker"},{"attributes":{"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"f35fb413-3a07-4fb8-9c10-2367c2709b16","type":"SaveTool"},{"attributes":{"items":[{"id":"10a521c3-1f69-432c-b3d2-d7d13ca60fab","type":"LegendItem"},{"id":"6317df25-82a4-4993-810d-5d125249037e","type":"LegendItem"},{"id":"b15f80d0-9a95-4220-9fb0-8c4a1580dfb4","type":"LegendItem"}],"orientation":"horizontal","plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"bfefdfeb-8826-48b1-9a88-7dbd98f6de82","type":"Legend"},{"attributes":{"grid_line_alpha":{"value":0.5},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"ticker":{"id":"8654eb6a-1e02-4506-b86a-bcd84e471080","type":"BasicTicker"}},"id":"951cabcb-14a5-4601-9795-5f0f440a1e1f","type":"Grid"},{"attributes":{"children":[{"id":"cde86eb4-413c-477e-8b03-38d93edc0f47","type":"Row"}]},"id":"784f5132-6f87-4a69-85c7-8d4eb9ac6d48","type":"Column"},{"attributes":{"line_color":{"value":"#ff7f0e"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"040b41a0-d154-45fa-9230-a174ebf98b72","type":"Line"},{"attributes":{"label":{"value":"Infected"},"renderers":[{"id":"2f291fbf-aa58-403b-9656-c032207caf75","type":"GlyphRenderer"}]},"id":"996c6dba-dc48-489d-8445-a83ce75ea7b5","type":"LegendItem"},{"attributes":{},"id":"098eff25-f41e-40b4-9aca-f1206151a05b","type":"BasicTickFormatter"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"214731b7-c8fa-4871-8d0f-2c4e985f0b87","type":"Line"},{"attributes":{"data_source":{"id":"6139dedd-1e8a-4f6c-b4d2-607e4f1d9af7","type":"ColumnDataSource"},"glyph":{"id":"91975a66-63d3-4725-afa5-830b12350508","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"5fc4ca7a-5eee-4433-9e92-a856648ee14a","type":"Line"},"selection_glyph":null},"id":"9a7f6e31-fdbe-42bb-a2f0-eee8815c6f2f","type":"GlyphRenderer"},{"attributes":{"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"6d0e21da-9942-42a2-a49c-89ac1ee187ac","type":"Line"},{"attributes":{"axis_label":"Iterations","formatter":{"id":"9056b210-7c99-4fea-9629-54a0f9d79a33","type":"BasicTickFormatter"},"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"},"ticker":{"id":"0630c29f-b2da-4de4-b653-19a543d21893","type":"BasicTicker"}},"id":"15653d31-9be8-45f5-b943-a4b5cb0f49d2","type":"LinearAxis"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"c6e3a379-610d-45d6-96b2-f732a2e94e6e","type":"WheelZoomTool"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"1ef72fa5-2382-4fc5-a70b-1c801cb7076d","type":"HelpTool"},{"attributes":{"active_drag":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"22d6c60f-32b1-4e56-8e29-af02ddf563c8","type":"PanTool"},{"id":"c6994d32-768a-4694-b002-5b091ad62bd4","type":"WheelZoomTool"},{"id":"b8f252e3-1b81-4110-9364-c8743b91ee83","type":"BoxZoomTool"},{"id":"f35fb413-3a07-4fb8-9c10-2367c2709b16","type":"SaveTool"},{"id":"c4930aa1-9bb3-4a16-b89e-7a1ba5df51ba","type":"ResetTool"},{"id":"faf78620-c3dd-414a-b76b-ce9a46cba6eb","type":"HelpTool"}]},"id":"ed8a0a5d-21c7-45bb-803d-1baa1407b58f","type":"Toolbar"},{"attributes":{"overlay":{"id":"33084629-22b5-4627-af22-7ee4d15df4ab","type":"BoxAnnotation"},"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}},"id":"b8f252e3-1b81-4110-9364-c8743b91ee83","type":"BoxZoomTool"},{"attributes":{"label":{"value":"Removed"},"renderers":[{"id":"c9426e74-3afd-45c1-8aa8-e385731b8da2","type":"GlyphRenderer"}]},"id":"bd422dde-b71e-4c36-b31d-80b27c2abe2c","type":"LegendItem"},{"attributes":{"data_source":{"id":"6517ac4d-6086-415b-96c5-65c3f26d9295","type":"ColumnDataSource"},"glyph":{"id":"54251b77-5d2c-4d87-8d0b-430044aec53b","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"a5b7eddd-bbe5-4157-93b1-c453c43d6fe3","type":"Line"},"selection_glyph":null},"id":"b2e45137-0318-4568-935c-507665224e53","type":"GlyphRenderer"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[950,943,936,927,921,911,904,897,888,879,870,862,851,840,828,816,804,789,772,754,741,726,707,684,663,636,606,580,565,536,510,484,466,446,419,397,373,343,328,311,292,269,252,245,227,208,194,187,173,161,147,142,139,131,118,105,99,91,84,82,79,75,70,66,65,62,59,47,44,41,37,35,34,32,31,30,29,28,26,25,23,20,19,19,17,17,17,16,15,15,13,12,12,11,11,10,10,9,9,9,9,9,9,9,8,8,7,7,7,7,7,6,6,6,6,6,6,6,6,6,5,5,4,4,4,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]}},"id":"5acb4cd5-c097-479c-bdc3-4d7fce2974ec","type":"ColumnDataSource"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"5fc4ca7a-5eee-4433-9e92-a856648ee14a","type":"Line"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[50,55,62,71,75,85,89,96,105,112,120,127,138,149,160,171,181,194,209,224,235,249,265,286,306,330,359,380,389,413,436,455,467,483,502,521,541,564,571,584,591,610,618,619,630,644,656,657,664,667,673,673,672,671,675,683,686,684,679,674,673,674,668,669,666,665,661,667,658,651,648,639,631,627,626,621,617,614,607,603,602,597,592,580,575,565,562,558,551,542,534,532,527,522,518,518,503,500,494,491,482,479,473,467,466,464,461,458,454,449,447,442,438,433,431,430,425,420,414,412,413,412,408,401,397,392,387,379,376,374,373,364,362,358,353,351,346,343,339,337,331,325,321,315,312,309,305,300,296,294,291,288,284,283,279,279,278,275,271,270,265,261,257,254,252,250,245,243,241,239,239,235,234,233,230,228,227,226,224,223,217,214,213,212,210,207,201,199,196,192,190,185,181,178,175,171,170,170,168,167]}},"id":"6d2ade8c-5a1f-4d07-a7d6-0a58bd25f973","type":"ColumnDataSource"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"48376b2c-7869-4a12-a480-c577074066c2","type":"PanTool"},{"attributes":{},"id":"32184b0f-dd31-489e-af88-98ba58a2b8ac","type":"BasicTicker"},{"attributes":{"children":[{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"}]},"id":"cde86eb4-413c-477e-8b03-38d93edc0f47","type":"Row"},{"attributes":{"callback":null},"id":"85b05a36-5d74-47b4-971b-9605a2df9a7f","type":"DataRange1d"},{"attributes":{"dimension":1,"grid_line_alpha":{"value":0.5},"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"},"ticker":{"id":"2283b2bd-c777-411a-9aaa-525e09bbc60e","type":"BasicTicker"}},"id":"4ba26872-123e-4db2-9f54-8733982dce41","type":"Grid"},{"attributes":{},"id":"0630c29f-b2da-4de4-b653-19a543d21893","type":"BasicTicker"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198],"y":[-6,-6,-7,-5,-10,-5,-5,-8,-7,-7,-7,-11,-10,-10,-9,-5,-13,-12,-13,-10,-15,-17,-17,-18,-17,-23,-19,-6,-22,-17,-15,-10,-13,-15,-18,-18,-18,-5,-10,-5,-13,-5,1,-7,-11,-8,2,-6,0,-4,1,1,1,0,-7,0,1,6,5,2,0,5,2,2,1,4,-4,9,5,4,9,8,4,1,5,3,3,7,5,1,6,6,12,6,10,3,5,7,9,8,2,4,6,4,1,14,3,5,3,9,3,6,6,2,2,3,3,4,5,2,5,4,4,2,1,5,5,6,2,0,1,5,7,4,5,5,8,4,2,1,8,2,4,5,2,4,3,3,2,6,6,4,6,3,3,3,5,3,2,3,3,4,1,4,0,1,2,4,1,5,4,3,3,2,2,5,2,2,2,0,4,1,1,3,2,1,1,1,1,5,3,1,1,2,3,6,2,3,4,2,5,4,2,3,4,1,0,2,1]}},"id":"6517ac4d-6086-415b-96c5-65c3f26d9295","type":"ColumnDataSource"},{"attributes":{},"id":"a4c444ea-afe2-42ff-934e-8221368e5123","type":"ToolEvents"},{"attributes":{"callback":null},"id":"b035140b-eb4e-4e76-bb04-021785201d9e","type":"DataRange1d"},{"attributes":{"overlay":{"id":"2aa729d3-0267-4b47-9c86-ae38a1666c11","type":"BoxAnnotation"},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"1af75cd2-afd0-4bb2-ac55-afc6a5c2ca33","type":"BoxZoomTool"},{"attributes":{"dimension":1,"grid_line_alpha":{"value":0.5},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"ticker":{"id":"32184b0f-dd31-489e-af88-98ba58a2b8ac","type":"BasicTicker"}},"id":"ce449e57-2c0e-4bcf-b58d-674abde975a9","type":"Grid"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[0,2,2,2,4,4,7,7,7,9,10,11,11,11,12,13,15,17,19,22,24,25,28,30,31,34,35,40,46,51,54,61,67,71,79,82,86,93,101,105,117,121,130,136,143,148,150,156,163,172,180,185,189,198,207,212,215,225,237,244,248,251,262,265,269,273,280,286,298,308,315,326,335,341,343,349,354,358,367,372,375,383,389,401,408,418,421,426,434,443,453,456,461,467,471,472,487,491,497,500,509,512,518,524,526,528,532,535,539,544,546,552,556,561,563,564,569,574,580,582,582,583,588,595,599,605,610,618,622,624,625,634,636,640,645,647,652,655,659,661,667,673,677,683,686,689,693,698,702,704,707,710,714,715,719,719,720,723,727,728,733,737,741,744,746,748,753,755,757,759,759,763,764,765,768,770,771,772,774,775,781,784,785,786,788,791,797,799,802,806,808,813,817,820,823,827,828,828,830,831]}},"id":"c78ad910-d6a7-40ca-a9a7-44b214e1be06","type":"ColumnDataSource"},{"attributes":{},"id":"8654eb6a-1e02-4506-b86a-bcd84e471080","type":"BasicTicker"},{"attributes":{"below":[{"id":"15653d31-9be8-45f5-b943-a4b5cb0f49d2","type":"LinearAxis"},{"id":"50441167-2012-44bb-9920-8c01326d546a","type":"Title"}],"left":[{"id":"dd134c98-c27b-4ebd-b7ab-2747cf3fd7bd","type":"LinearAxis"}],"plot_height":400,"plot_width":400,"renderers":[{"id":"15653d31-9be8-45f5-b943-a4b5cb0f49d2","type":"LinearAxis"},{"id":"c61dddae-a1ce-49e4-b219-37460871295a","type":"Grid"},{"id":"dd134c98-c27b-4ebd-b7ab-2747cf3fd7bd","type":"LinearAxis"},{"id":"4ba26872-123e-4db2-9f54-8733982dce41","type":"Grid"},{"id":"33084629-22b5-4627-af22-7ee4d15df4ab","type":"BoxAnnotation"},{"id":"bfefdfeb-8826-48b1-9a88-7dbd98f6de82","type":"Legend"},{"id":"fe6fd0de-7efd-4b79-ab5c-1e90566cfe6a","type":"GlyphRenderer"},{"id":"9a7f6e31-fdbe-42bb-a2f0-eee8815c6f2f","type":"GlyphRenderer"},{"id":"b2e45137-0318-4568-935c-507665224e53","type":"GlyphRenderer"},{"id":"50441167-2012-44bb-9920-8c01326d546a","type":"Title"}],"title":{"id":"33aa9349-96bc-49ba-a6ec-745f6116860d","type":"Title"},"tool_events":{"id":"4d5ad420-3d61-416d-9d1e-91cd959bebbf","type":"ToolEvents"},"toolbar":{"id":"ed8a0a5d-21c7-45bb-803d-1baa1407b58f","type":"Toolbar"},"toolbar_location":null,"x_range":{"id":"85b05a36-5d74-47b4-971b-9605a2df9a7f","type":"DataRange1d"},"y_range":{"id":"0086e3a7-c3c5-4db1-99e0-8fee7b1f2eaf","type":"DataRange1d"}},"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"},{"attributes":{"axis_label":"#Delta Nodes","formatter":{"id":"a4c4e9c9-adf9-43fe-bc53-f0b02588f29e","type":"BasicTickFormatter"},"plot":{"id":"2fdf096c-378c-4b73-8ecc-dcba5bc1ca02","subtype":"Figure","type":"Plot"},"ticker":{"id":"2283b2bd-c777-411a-9aaa-525e09bbc60e","type":"BasicTicker"}},"id":"dd134c98-c27b-4ebd-b7ab-2747cf3fd7bd","type":"LinearAxis"},{"attributes":{"axis_label":"Iterations","formatter":{"id":"098eff25-f41e-40b4-9aca-f1206151a05b","type":"BasicTickFormatter"},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"ticker":{"id":"8654eb6a-1e02-4506-b86a-bcd84e471080","type":"BasicTicker"}},"id":"39ccff6f-cdcf-4ddb-a0b5-fa52ad5425f5","type":"LinearAxis"},{"attributes":{"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"2573568d-59d5-4dc4-8400-58d6572df9ee","type":"Line"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"53498048-937f-435c-9e55-c246830e877b","type":"ResetTool"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"04fddfc5-afdf-464e-8768-4d0b3ce5f876","type":"Line"},{"attributes":{"label":{"value":"Infected"},"renderers":[{"id":"9a7f6e31-fdbe-42bb-a2f0-eee8815c6f2f","type":"GlyphRenderer"}]},"id":"6317df25-82a4-4993-810d-5d125249037e","type":"LegendItem"},{"attributes":{"data_source":{"id":"5acb4cd5-c097-479c-bdc3-4d7fce2974ec","type":"ColumnDataSource"},"glyph":{"id":"2573568d-59d5-4dc4-8400-58d6572df9ee","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"214731b7-c8fa-4871-8d0f-2c4e985f0b87","type":"Line"},"selection_glyph":null},"id":"ab15b2c1-2506-4559-b296-0444a1a4df10","type":"GlyphRenderer"},{"attributes":{"sizing_mode":"scale_width","toolbar_location":"above","tools":[{"id":"48376b2c-7869-4a12-a480-c577074066c2","type":"PanTool"},{"id":"c6e3a379-610d-45d6-96b2-f732a2e94e6e","type":"WheelZoomTool"},{"id":"1af75cd2-afd0-4bb2-ac55-afc6a5c2ca33","type":"BoxZoomTool"},{"id":"70c0ee7e-500b-49a2-af4b-44a42dd82cda","type":"SaveTool"},{"id":"53498048-937f-435c-9e55-c246830e877b","type":"ResetTool"},{"id":"1ef72fa5-2382-4fc5-a70b-1c801cb7076d","type":"HelpTool"},{"id":"22d6c60f-32b1-4e56-8e29-af02ddf563c8","type":"PanTool"},{"id":"c6994d32-768a-4694-b002-5b091ad62bd4","type":"WheelZoomTool"},{"id":"b8f252e3-1b81-4110-9364-c8743b91ee83","type":"BoxZoomTool"},{"id":"f35fb413-3a07-4fb8-9c10-2367c2709b16","type":"SaveTool"},{"id":"c4930aa1-9bb3-4a16-b89e-7a1ba5df51ba","type":"ResetTool"},{"id":"faf78620-c3dd-414a-b76b-ce9a46cba6eb","type":"HelpTool"}]},"id":"52049298-0a93-4f82-9c9c-3d23300a4dd9","type":"ToolbarBox"},{"attributes":{"label":{"value":"Susceptible"},"renderers":[{"id":"fe6fd0de-7efd-4b79-ab5c-1e90566cfe6a","type":"GlyphRenderer"}]},"id":"10a521c3-1f69-432c-b3d2-d7d13ca60fab","type":"LegendItem"},{"attributes":{"active_drag":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"48376b2c-7869-4a12-a480-c577074066c2","type":"PanTool"},{"id":"c6e3a379-610d-45d6-96b2-f732a2e94e6e","type":"WheelZoomTool"},{"id":"1af75cd2-afd0-4bb2-ac55-afc6a5c2ca33","type":"BoxZoomTool"},{"id":"70c0ee7e-500b-49a2-af4b-44a42dd82cda","type":"SaveTool"},{"id":"53498048-937f-435c-9e55-c246830e877b","type":"ResetTool"},{"id":"1ef72fa5-2382-4fc5-a70b-1c801cb7076d","type":"HelpTool"}]},"id":"fff415bf-dbc0-441a-a759-dc72f26c8b4f","type":"Toolbar"},{"attributes":{},"id":"a4c4e9c9-adf9-43fe-bc53-f0b02588f29e","type":"BasicTickFormatter"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"de0f30d8-f393-47ea-95bd-2a8828bd3f36","type":"Line"}],"root_ids":["0fd11d07-cc0c-405b-961b-eb00748838c0"]},"title":"Bokeh Application","version":"0.12.4"}};
                var render_items = [{"docid":"053faff6-6e76-4cc8-b281-fc58aac2842a","elementid":"c6021a60-5b3a-4383-8ab9-4f07cf593a91","modelid":"0fd11d07-cc0c-405b-961b-eb00748838c0"}];
                
                Bokeh.embed.embed_items(docs_json, render_items);
              };
              if (document.readyState != "loading") fn();
              else document.addEventListener("DOMContentLoaded", fn);
            })();
          },
          function(Bokeh) {
          }
        ];
      
        function run_inline_js() {
          
          if ((window.Bokeh !== undefined) || (force === true)) {
            for (var i = 0; i < inline_js.length; i++) {
              inline_js[i](window.Bokeh);
            }if (force === true) {
              display_loaded();
            }} else if (Date.now() < window._bokeh_timeout) {
            setTimeout(run_inline_js, 100);
          } else if (!window._bokeh_failed_load) {
            console.log("Bokeh: BokehJS failed to load within specified timeout.");
            window._bokeh_failed_load = true;
          } else if (force !== true) {
            var cell = $(document.getElementById("c6021a60-5b3a-4383-8ab9-4f07cf593a91")).parents('.cell').data().cell;
            cell.output_area.append_execute_result(NB_LOAD_WARNING)
          }
      
        }
      
        if (window._bokeh_is_loading === 0) {
          console.log("Bokeh: BokehJS loaded, going straight to plotting");
          run_inline_js();
        } else {
          load_libs(js_urls, function() {
            console.log("Bokeh: BokehJS plotting callback run at", now());
            run_inline_js();
          });
        }
      }(this));
    </script>


Multiplots are also useful to compare different diffusion models applied
to the same graph (as well as a same model instantiated with different
parameters)

.. code:: python

    import ndlib.models.epidemics.SISModel as sis
    import ndlib.models.epidemics.SIModel as si
    import ndlib.models.epidemics.ThresholdModel as th
    
    vm = MultiPlot()
    vm.add_plot(p)
    
    # SIS
    sis_model = sis.SISModel(g)
    config = mc.Configuration()
    config.add_model_parameter('beta', 0.001)
    config.add_model_parameter('lambda', 0.01)
    config.add_model_parameter("percentage_infected", 0.05)
    sis_model.set_initial_status(config)
    iterations = sis_model.iteration_bunch(200)
    viz = DiffusionTrend(sis_model, iterations)
    p3 = viz.plot(width=400, height=400)
    vm.add_plot(p3)
    
    # SI
    si_model = si.SIModel(g)
    config = mc.Configuration()
    config.add_model_parameter('beta', 0.001)
    config.add_model_parameter("percentage_infected", 0.05)
    si_model.set_initial_status(config)
    iterations = si_model.iteration_bunch(200)
    viz = DiffusionTrend(si_model, iterations)
    p4 = viz.plot(width=400, height=400)
    vm.add_plot(p4)
    
    # Threshold
    th_model = th.ThresholdModel(g)
    config = mc.Configuration()
    
    # Set individual node threshold
    threshold = 0.40
    for n in g.nodes():
        config.add_node_configuration("threshold", n, threshold)
    
    config.add_model_parameter("percentage_infected", 0.30)
    th_model.set_initial_status(config)
    iterations = th_model.iteration_bunch(60)
    viz = DiffusionTrend(th_model, iterations)
    p5 = viz.plot(width=400, height=400)
    vm.add_plot(p5)
    
    m = vm.plot()
    show(m)



.. raw:: html

    
    
        <div class="bk-root">
            <div class="bk-plotdiv" id="d4504979-9a6d-4461-ae24-75391fedd712"></div>
        </div>
    <script type="text/javascript">
      
      (function(global) {
        function now() {
          return new Date();
        }
      
        var force = false;
      
        if (typeof (window._bokeh_onload_callbacks) === "undefined" || force === true) {
          window._bokeh_onload_callbacks = [];
          window._bokeh_is_loading = undefined;
        }
      
      
        
        if (typeof (window._bokeh_timeout) === "undefined" || force === true) {
          window._bokeh_timeout = Date.now() + 0;
          window._bokeh_failed_load = false;
        }
      
        var NB_LOAD_WARNING = {'data': {'text/html':
           "<div style='background-color: #fdd'>\n"+
           "<p>\n"+
           "BokehJS does not appear to have successfully loaded. If loading BokehJS from CDN, this \n"+
           "may be due to a slow or bad network connection. Possible fixes:\n"+
           "</p>\n"+
           "<ul>\n"+
           "<li>re-rerun `output_notebook()` to attempt to load from CDN again, or</li>\n"+
           "<li>use INLINE resources instead, as so:</li>\n"+
           "</ul>\n"+
           "<code>\n"+
           "from bokeh.resources import INLINE\n"+
           "output_notebook(resources=INLINE)\n"+
           "</code>\n"+
           "</div>"}};
      
        function display_loaded() {
          if (window.Bokeh !== undefined) {
            document.getElementById("d4504979-9a6d-4461-ae24-75391fedd712").textContent = "BokehJS successfully loaded.";
          } else if (Date.now() < window._bokeh_timeout) {
            setTimeout(display_loaded, 100)
          }
        }
      
        function run_callbacks() {
          window._bokeh_onload_callbacks.forEach(function(callback) { callback() });
          delete window._bokeh_onload_callbacks
          console.info("Bokeh: all callbacks have finished");
        }
      
        function load_libs(js_urls, callback) {
          window._bokeh_onload_callbacks.push(callback);
          if (window._bokeh_is_loading > 0) {
            console.log("Bokeh: BokehJS is being loaded, scheduling callback at", now());
            return null;
          }
          if (js_urls == null || js_urls.length === 0) {
            run_callbacks();
            return null;
          }
          console.log("Bokeh: BokehJS not loaded, scheduling load and callback at", now());
          window._bokeh_is_loading = js_urls.length;
          for (var i = 0; i < js_urls.length; i++) {
            var url = js_urls[i];
            var s = document.createElement('script');
            s.src = url;
            s.async = false;
            s.onreadystatechange = s.onload = function() {
              window._bokeh_is_loading--;
              if (window._bokeh_is_loading === 0) {
                console.log("Bokeh: all BokehJS libraries loaded");
                run_callbacks()
              }
            };
            s.onerror = function() {
              console.warn("failed to load library " + url);
            };
            console.log("Bokeh: injecting script tag for BokehJS library: ", url);
            document.getElementsByTagName("head")[0].appendChild(s);
          }
        };var element = document.getElementById("d4504979-9a6d-4461-ae24-75391fedd712");
        if (element == null) {
          console.log("Bokeh: ERROR: autoload.js configured with elementid 'd4504979-9a6d-4461-ae24-75391fedd712' but no matching script tag was found. ")
          return false;
        }
      
        var js_urls = [];
      
        var inline_js = [
          function(Bokeh) {
            (function() {
              var fn = function() {
                var docs_json = {"36bb618b-1d3c-4ebf-a033-48c469ebc39a":{"roots":{"references":[{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"cf48a48b-ff18-4905-ba87-0410081f5de5","type":"Line"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[50,55,62,71,75,85,89,96,105,112,120,127,138,149,160,171,181,194,209,224,235,249,265,286,306,330,359,380,389,413,436,455,467,483,502,521,541,564,571,584,591,610,618,619,630,644,656,657,664,667,673,673,672,671,675,683,686,684,679,674,673,674,668,669,666,665,661,667,658,651,648,639,631,627,626,621,617,614,607,603,602,597,592,580,575,565,562,558,551,542,534,532,527,522,518,518,503,500,494,491,482,479,473,467,466,464,461,458,454,449,447,442,438,433,431,430,425,420,414,412,413,412,408,401,397,392,387,379,376,374,373,364,362,358,353,351,346,343,339,337,331,325,321,315,312,309,305,300,296,294,291,288,284,283,279,279,278,275,271,270,265,261,257,254,252,250,245,243,241,239,239,235,234,233,230,228,227,226,224,223,217,214,213,212,210,207,201,199,196,192,190,185,181,178,175,171,170,170,168,167]}},"id":"6d2ade8c-5a1f-4d07-a7d6-0a58bd25f973","type":"ColumnDataSource"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"2433a5a8-f98c-4771-8aeb-b952443305a7","type":"Line"},{"attributes":{"plot":{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"}},"id":"40397fa0-9069-4b25-8b6b-49a1f022e535","type":"WheelZoomTool"},{"attributes":{"line_color":{"value":"#aec7e8"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"a4961edf-730d-4b8d-9ac3-8507bb29d046","type":"Line"},{"attributes":{"callback":null},"id":"ea587e60-89b0-4fb1-babf-51652049472c","type":"DataRange1d"},{"attributes":{"plot":{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"}},"id":"34a99321-e6d3-41b7-9d1c-89f40ca4ed50","type":"HelpTool"},{"attributes":{"label":{"value":"Infected"},"renderers":[{"id":"6c0583e0-ea13-49e6-b5b0-4076ca00c493","type":"GlyphRenderer"}]},"id":"49032db6-b202-4ecb-b8d0-2742b244630a","type":"LegendItem"},{"attributes":{"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"2c74dbb3-8db4-4ee9-9097-7ce894a8136a","type":"Line"},{"attributes":{"label":{"value":"Infected"},"renderers":[{"id":"fa1dc348-ba35-4d96-abb3-8ea86458175d","type":"GlyphRenderer"}]},"id":"939623cc-09f4-40d7-8f8d-f51d9eb49340","type":"LegendItem"},{"attributes":{"children":[{"id":"93974615-c7f5-420c-a19a-7bc58ea0a9cf","type":"Row"},{"id":"9210daa5-140c-44e4-ae99-fa50be008597","type":"Row"}]},"id":"2fac130c-e10a-48d2-b9f5-3603dd245d72","type":"Column"},{"attributes":{"axis_label":"#Nodes","formatter":{"id":"a85fcbfc-ce33-471d-b81c-9f3db5169de5","type":"BasicTickFormatter"},"plot":{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"},"ticker":{"id":"895ec219-2396-44cc-80a9-5c6f3730f47d","type":"BasicTicker"}},"id":"417d9953-84bf-4966-b3d4-924fbf4758cb","type":"LinearAxis"},{"attributes":{"callback":null},"id":"676e91bc-7212-4e2c-b653-193e08d8f7ca","type":"DataRange1d"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59],"y":[300,319,336,358,407,619,999,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]}},"id":"98a08cf6-efd8-4cd0-b2c3-6d40d2cde539","type":"ColumnDataSource"},{"attributes":{"items":[{"id":"fd0e5876-71c4-45e3-a1e5-218fd3d27f8a","type":"LegendItem"},{"id":"939623cc-09f4-40d7-8f8d-f51d9eb49340","type":"LegendItem"}],"orientation":"horizontal","plot":{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"}},"id":"61acbbd4-1485-4f99-a066-1d8f4285fb7e","type":"Legend"},{"attributes":{"plot":{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"}},"id":"7d89ad74-e3c7-47c4-b1d7-211465866df4","type":"PanTool"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"618e4fe0-06fb-4624-891f-07e7d3d7c9ab","type":"BoxAnnotation"},{"attributes":{"callback":null},"id":"f09408a8-5aa9-443c-ac55-134c4f66ea87","type":"DataRange1d"},{"attributes":{"plot":{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"}},"id":"f9dc54f1-b812-4f9b-9e2f-25076904bf5f","type":"ResetTool"},{"attributes":{"sizing_mode":"scale_width","toolbar_location":"above","tools":[{"id":"48376b2c-7869-4a12-a480-c577074066c2","type":"PanTool"},{"id":"c6e3a379-610d-45d6-96b2-f732a2e94e6e","type":"WheelZoomTool"},{"id":"1af75cd2-afd0-4bb2-ac55-afc6a5c2ca33","type":"BoxZoomTool"},{"id":"70c0ee7e-500b-49a2-af4b-44a42dd82cda","type":"SaveTool"},{"id":"53498048-937f-435c-9e55-c246830e877b","type":"ResetTool"},{"id":"1ef72fa5-2382-4fc5-a70b-1c801cb7076d","type":"HelpTool"},{"id":"7d89ad74-e3c7-47c4-b1d7-211465866df4","type":"PanTool"},{"id":"525835dd-eaf0-4fc1-a085-dfc8fd0d4e77","type":"WheelZoomTool"},{"id":"fbb31755-ea84-4ea9-b46f-c9c3d2a713cb","type":"BoxZoomTool"},{"id":"00e84a3b-1996-4796-bb08-90d166034084","type":"SaveTool"},{"id":"2a1874fb-5f1f-447d-87c9-7b306a3083c8","type":"ResetTool"},{"id":"34a99321-e6d3-41b7-9d1c-89f40ca4ed50","type":"HelpTool"},{"id":"7a493979-47d8-48fb-b0c9-3b0514ca40b7","type":"PanTool"},{"id":"65d1697b-7863-4fd0-ac3a-031aa735b348","type":"WheelZoomTool"},{"id":"4a5705cd-92f0-4fac-95c7-345feae188a2","type":"BoxZoomTool"},{"id":"c0668b37-8b41-41f1-bd84-0872250d0fae","type":"SaveTool"},{"id":"f9dc54f1-b812-4f9b-9e2f-25076904bf5f","type":"ResetTool"},{"id":"d4b743be-890a-46f6-9893-d8ffa12ece44","type":"HelpTool"},{"id":"0cfa6c6c-b98b-4baa-b07b-b63804ba22fc","type":"PanTool"},{"id":"40397fa0-9069-4b25-8b6b-49a1f022e535","type":"WheelZoomTool"},{"id":"0bd57782-9b74-4a40-a68a-65721e6b21e9","type":"BoxZoomTool"},{"id":"d8cebb2c-fcc2-425e-9b5e-1b686f53bbf0","type":"SaveTool"},{"id":"e3858e3e-80ac-41d0-b4ca-d00cbdf60c02","type":"ResetTool"},{"id":"70c698ca-1c84-4677-981f-0e933efb7a2e","type":"HelpTool"}]},"id":"766fcce5-5005-4100-b690-10bd58a33ad5","type":"ToolbarBox"},{"attributes":{"label":{"value":"Susceptible"},"renderers":[{"id":"ecd60fd7-a26c-444e-abf4-e6039d2ce966","type":"GlyphRenderer"}]},"id":"fd0e5876-71c4-45e3-a1e5-218fd3d27f8a","type":"LegendItem"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"b44affcc-934e-4418-b560-2c4f12c41205","type":"BoxAnnotation"},{"attributes":{"plot":{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"}},"id":"0cfa6c6c-b98b-4baa-b07b-b63804ba22fc","type":"PanTool"},{"attributes":{},"id":"9f2cbfb1-f808-43bc-83bb-09c0274e6c89","type":"ToolEvents"},{"attributes":{"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"2573568d-59d5-4dc4-8400-58d6572df9ee","type":"Line"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"53498048-937f-435c-9e55-c246830e877b","type":"ResetTool"},{"attributes":{"callback":null},"id":"0d300f4e-a2ff-4925-9117-f2f32e649f0d","type":"DataRange1d"},{"attributes":{"plot":null,"text":"Threshold - Diffusion Trend"},"id":"87000631-a09a-461c-bf53-948cf9e2acf9","type":"Title"},{"attributes":{"active_drag":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"7a493979-47d8-48fb-b0c9-3b0514ca40b7","type":"PanTool"},{"id":"65d1697b-7863-4fd0-ac3a-031aa735b348","type":"WheelZoomTool"},{"id":"4a5705cd-92f0-4fac-95c7-345feae188a2","type":"BoxZoomTool"},{"id":"c0668b37-8b41-41f1-bd84-0872250d0fae","type":"SaveTool"},{"id":"f9dc54f1-b812-4f9b-9e2f-25076904bf5f","type":"ResetTool"},{"id":"d4b743be-890a-46f6-9893-d8ffa12ece44","type":"HelpTool"}]},"id":"a0fec24f-65f5-4aec-a161-62cb579dc496","type":"Toolbar"},{"attributes":{"callback":null},"id":"9dabb2ef-f9e4-419b-a3ba-e85ee9c7312a","type":"DataRange1d"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"70c0ee7e-500b-49a2-af4b-44a42dd82cda","type":"SaveTool"},{"attributes":{},"id":"4d707cfb-90ba-4533-b076-a0f6b88bc0d7","type":"BasicTickFormatter"},{"attributes":{"items":[{"id":"909ac954-0acd-40b7-8797-da82af402b4a","type":"LegendItem"},{"id":"996c6dba-dc48-489d-8445-a83ce75ea7b5","type":"LegendItem"},{"id":"bd422dde-b71e-4c36-b31d-80b27c2abe2c","type":"LegendItem"}],"orientation":"horizontal","plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"4b1db386-6e2c-4f05-b333-c37d2ee5a870","type":"Legend"},{"attributes":{"children":[{"id":"766fcce5-5005-4100-b690-10bd58a33ad5","type":"ToolbarBox"},{"id":"2fac130c-e10a-48d2-b9f5-3603dd245d72","type":"Column"}]},"id":"df321518-6e67-4286-b70a-a05e23a97a5e","type":"Column"},{"attributes":{"align":"center","plot":{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"},"text":"percentage infected: 0.05, beta: 0.001"},"id":"b8c7de88-eb27-44d7-8f92-9952fdef32bc","type":"Title"},{"attributes":{"data_source":{"id":"6d2ade8c-5a1f-4d07-a7d6-0a58bd25f973","type":"ColumnDataSource"},"glyph":{"id":"485837af-4003-481d-9e3b-22c770c076ed","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"de0f30d8-f393-47ea-95bd-2a8828bd3f36","type":"Line"},"selection_glyph":null},"id":"2f291fbf-aa58-403b-9656-c032207caf75","type":"GlyphRenderer"},{"attributes":{"plot":{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"}},"id":"00e84a3b-1996-4796-bb08-90d166034084","type":"SaveTool"},{"attributes":{},"id":"84ebdd3d-7723-4683-8092-1ba79733178d","type":"BasicTickFormatter"},{"attributes":{"grid_line_alpha":{"value":0.5},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"ticker":{"id":"8654eb6a-1e02-4506-b86a-bcd84e471080","type":"BasicTicker"}},"id":"951cabcb-14a5-4601-9795-5f0f440a1e1f","type":"Grid"},{"attributes":{"below":[{"id":"a9cc4998-4710-4b0d-8768-831b6ad8fa1e","type":"LinearAxis"},{"id":"cb412e46-b85a-4a8e-8bfd-a8e13b284339","type":"Title"}],"left":[{"id":"a29a44a2-0fb0-45ae-863e-f19bb23eb83a","type":"LinearAxis"}],"plot_height":400,"plot_width":400,"renderers":[{"id":"a9cc4998-4710-4b0d-8768-831b6ad8fa1e","type":"LinearAxis"},{"id":"2a436908-e61f-4868-a934-b2899c087fb9","type":"Grid"},{"id":"a29a44a2-0fb0-45ae-863e-f19bb23eb83a","type":"LinearAxis"},{"id":"6748f238-258b-48a6-81af-1adf97961852","type":"Grid"},{"id":"285373e3-c9bd-4926-b503-9bb5607195eb","type":"BoxAnnotation"},{"id":"73373dd3-d3da-4db4-a02c-2b542baae787","type":"Legend"},{"id":"ad955bdd-ea9b-4711-a851-b915321b851f","type":"GlyphRenderer"},{"id":"6c0583e0-ea13-49e6-b5b0-4076ca00c493","type":"GlyphRenderer"},{"id":"cb412e46-b85a-4a8e-8bfd-a8e13b284339","type":"Title"}],"title":{"id":"9d9ac742-dde3-41ee-8ed4-e4fd33e2d558","type":"Title"},"tool_events":{"id":"cce981aa-7095-4762-b38c-b464702ac9b3","type":"ToolEvents"},"toolbar":{"id":"7db71631-a724-4e90-a2bc-7042a0cca896","type":"Toolbar"},"toolbar_location":null,"x_range":{"id":"0d300f4e-a2ff-4925-9117-f2f32e649f0d","type":"DataRange1d"},"y_range":{"id":"314e9b9d-09c4-426b-a260-7aa88578698f","type":"DataRange1d"}},"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"},{"attributes":{"grid_line_alpha":{"value":0.5},"plot":{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"},"ticker":{"id":"68707d39-0620-4576-9ced-7c8e9c8046db","type":"BasicTicker"}},"id":"2a436908-e61f-4868-a934-b2899c087fb9","type":"Grid"},{"attributes":{"data_source":{"id":"862aabc0-e84b-439d-a3c8-d5fe10fa0e90","type":"ColumnDataSource"},"glyph":{"id":"2c74dbb3-8db4-4ee9-9097-7ce894a8136a","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"84ab2ba5-6516-497c-9b73-1fbd79ff8604","type":"Line"},"selection_glyph":null},"id":"ad955bdd-ea9b-4711-a851-b915321b851f","type":"GlyphRenderer"},{"attributes":{"callback":null},"id":"caa68f54-c562-4cad-8614-dae40fbe354a","type":"DataRange1d"},{"attributes":{"plot":{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"}},"id":"65d1697b-7863-4fd0-ac3a-031aa735b348","type":"WheelZoomTool"},{"attributes":{"data_source":{"id":"1b6a3b6a-b2bb-498a-8e3c-6b20ae11761f","type":"ColumnDataSource"},"glyph":{"id":"4c47d451-c54c-4016-a9e9-5257ee7bc8e1","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"cf48a48b-ff18-4905-ba87-0410081f5de5","type":"Line"},"selection_glyph":null},"id":"c2b27855-16a0-466e-bff8-52af1b1342b6","type":"GlyphRenderer"},{"attributes":{"dimension":1,"grid_line_alpha":{"value":0.5},"plot":{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"},"ticker":{"id":"97a659f8-738c-44bc-8bfe-10725d0daa4e","type":"BasicTicker"}},"id":"6748f238-258b-48a6-81af-1adf97961852","type":"Grid"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[950,943,936,927,921,911,904,897,888,879,870,862,851,840,828,816,804,789,772,754,741,726,707,684,663,636,606,580,565,536,510,484,466,446,419,397,373,343,328,311,292,269,252,245,227,208,194,187,173,161,147,142,139,131,118,105,99,91,84,82,79,75,70,66,65,62,59,47,44,41,37,35,34,32,31,30,29,28,26,25,23,20,19,19,17,17,17,16,15,15,13,12,12,11,11,10,10,9,9,9,9,9,9,9,8,8,7,7,7,7,7,6,6,6,6,6,6,6,6,6,5,5,4,4,4,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]}},"id":"5acb4cd5-c097-479c-bdc3-4d7fce2974ec","type":"ColumnDataSource"},{"attributes":{"plot":{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"}},"id":"7a493979-47d8-48fb-b0c9-3b0514ca40b7","type":"PanTool"},{"attributes":{},"id":"98b75b1e-3039-492a-a631-a7417b9beb3e","type":"BasicTickFormatter"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"214731b7-c8fa-4871-8d0f-2c4e985f0b87","type":"Line"},{"attributes":{"plot":null,"text":"SIS - Diffusion Trend"},"id":"9d9ac742-dde3-41ee-8ed4-e4fd33e2d558","type":"Title"},{"attributes":{"axis_label":"#Nodes","formatter":{"id":"98b75b1e-3039-492a-a631-a7417b9beb3e","type":"BasicTickFormatter"},"plot":{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"},"ticker":{"id":"7c9995a4-51f7-4614-abc4-d134be4cbcec","type":"BasicTicker"}},"id":"4130607e-b687-45b2-a86e-9607a3bb9ee6","type":"LinearAxis"},{"attributes":{},"id":"97a659f8-738c-44bc-8bfe-10725d0daa4e","type":"BasicTicker"},{"attributes":{},"id":"ab9dc9d1-8e7d-45fd-adff-d0d65a02c8fa","type":"ToolEvents"},{"attributes":{"items":[{"id":"1bf92cab-4283-4000-be0e-4be39d8798bb","type":"LegendItem"},{"id":"4e0e023b-ea82-4a03-afdc-65314af23673","type":"LegendItem"}],"orientation":"horizontal","plot":{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"}},"id":"da97bce8-f1cf-40df-bd3d-0bfb4d7427e3","type":"Legend"},{"attributes":{"plot":null,"text":"SIR - Diffusion Trend"},"id":"783bec4f-5692-4e65-b5ad-d43a008640de","type":"Title"},{"attributes":{"line_color":{"value":"#ff7f0e"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"040b41a0-d154-45fa-9230-a174ebf98b72","type":"Line"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59],"y":[700,681,664,642,593,381,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}},"id":"1b6a3b6a-b2bb-498a-8e3c-6b20ae11761f","type":"ColumnDataSource"},{"attributes":{"data_source":{"id":"5acb4cd5-c097-479c-bdc3-4d7fce2974ec","type":"ColumnDataSource"},"glyph":{"id":"2573568d-59d5-4dc4-8400-58d6572df9ee","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"214731b7-c8fa-4871-8d0f-2c4e985f0b87","type":"Line"},"selection_glyph":null},"id":"ab15b2c1-2506-4559-b296-0444a1a4df10","type":"GlyphRenderer"},{"attributes":{"children":[{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"},{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"}]},"id":"9210daa5-140c-44e4-ae99-fa50be008597","type":"Row"},{"attributes":{},"id":"06f31848-16c6-4c6d-a35b-88df247cacfd","type":"BasicTicker"},{"attributes":{"dimension":1,"grid_line_alpha":{"value":0.5},"plot":{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"},"ticker":{"id":"895ec219-2396-44cc-80a9-5c6f3730f47d","type":"BasicTicker"}},"id":"5a71e431-4f7e-411a-810e-664860fc9aa8","type":"Grid"},{"attributes":{"data_source":{"id":"0cee5f04-0cb8-42c6-a32b-9a3a5c4d9d67","type":"ColumnDataSource"},"glyph":{"id":"29b375e5-9439-47fb-b5ae-af6b5906b2c3","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"32e36402-9f68-433e-b0c2-91c27c1456e0","type":"Line"},"selection_glyph":null},"id":"6c0583e0-ea13-49e6-b5b0-4076ca00c493","type":"GlyphRenderer"},{"attributes":{},"id":"cce981aa-7095-4762-b38c-b464702ac9b3","type":"ToolEvents"},{"attributes":{"align":"center","plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"text":"percentage infected: 0.05, beta: 0.001, gamma: 0.01"},"id":"cb87025e-3f3b-48a4-a1c0-aec9c8af3205","type":"Title"},{"attributes":{"below":[{"id":"39ccff6f-cdcf-4ddb-a0b5-fa52ad5425f5","type":"LinearAxis"},{"id":"cb87025e-3f3b-48a4-a1c0-aec9c8af3205","type":"Title"}],"left":[{"id":"7b1dace5-aaf9-462f-88b8-7f8feecbfb2d","type":"LinearAxis"}],"plot_height":400,"plot_width":400,"renderers":[{"id":"39ccff6f-cdcf-4ddb-a0b5-fa52ad5425f5","type":"LinearAxis"},{"id":"951cabcb-14a5-4601-9795-5f0f440a1e1f","type":"Grid"},{"id":"7b1dace5-aaf9-462f-88b8-7f8feecbfb2d","type":"LinearAxis"},{"id":"ce449e57-2c0e-4bcf-b58d-674abde975a9","type":"Grid"},{"id":"2aa729d3-0267-4b47-9c86-ae38a1666c11","type":"BoxAnnotation"},{"id":"4b1db386-6e2c-4f05-b333-c37d2ee5a870","type":"Legend"},{"id":"ab15b2c1-2506-4559-b296-0444a1a4df10","type":"GlyphRenderer"},{"id":"2f291fbf-aa58-403b-9656-c032207caf75","type":"GlyphRenderer"},{"id":"c9426e74-3afd-45c1-8aa8-e385731b8da2","type":"GlyphRenderer"},{"id":"cb87025e-3f3b-48a4-a1c0-aec9c8af3205","type":"Title"}],"title":{"id":"783bec4f-5692-4e65-b5ad-d43a008640de","type":"Title"},"tool_events":{"id":"a4c444ea-afe2-42ff-934e-8221368e5123","type":"ToolEvents"},"toolbar":{"id":"fff415bf-dbc0-441a-a759-dc72f26c8b4f","type":"Toolbar"},"toolbar_location":null,"x_range":{"id":"b035140b-eb4e-4e76-bb04-021785201d9e","type":"DataRange1d"},"y_range":{"id":"676e91bc-7212-4e2c-b653-193e08d8f7ca","type":"DataRange1d"}},"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},{"attributes":{"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"f6760ec5-ed90-4f6b-a389-b1c0f4f64f72","type":"Line"},{"attributes":{},"id":"2fc18aae-753e-4f4b-b4db-1fda66da8ffa","type":"BasicTickFormatter"},{"attributes":{"axis_label":"#Nodes","formatter":{"id":"2fc18aae-753e-4f4b-b4db-1fda66da8ffa","type":"BasicTickFormatter"},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"ticker":{"id":"32184b0f-dd31-489e-af88-98ba58a2b8ac","type":"BasicTicker"}},"id":"7b1dace5-aaf9-462f-88b8-7f8feecbfb2d","type":"LinearAxis"},{"attributes":{},"id":"895ec219-2396-44cc-80a9-5c6f3730f47d","type":"BasicTicker"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"2aa729d3-0267-4b47-9c86-ae38a1666c11","type":"BoxAnnotation"},{"attributes":{"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"4c47d451-c54c-4016-a9e9-5257ee7bc8e1","type":"Line"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"f1345f17-8a99-4ab9-a43a-ec2dea23342b","type":"Line"},{"attributes":{"plot":{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"}},"id":"70c698ca-1c84-4677-981f-0e933efb7a2e","type":"HelpTool"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"c6e3a379-610d-45d6-96b2-f732a2e94e6e","type":"WheelZoomTool"},{"attributes":{"children":[{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"}]},"id":"93974615-c7f5-420c-a19a-7bc58ea0a9cf","type":"Row"},{"attributes":{"below":[{"id":"38d28985-a4d0-420a-b16c-d05ad24ff24a","type":"LinearAxis"},{"id":"54250996-2d48-47c6-a734-b6c345acc82a","type":"Title"}],"left":[{"id":"4130607e-b687-45b2-a86e-9607a3bb9ee6","type":"LinearAxis"}],"plot_height":400,"plot_width":400,"renderers":[{"id":"38d28985-a4d0-420a-b16c-d05ad24ff24a","type":"LinearAxis"},{"id":"0a13ea5e-5ba2-484a-b808-b8fbfecfebc8","type":"Grid"},{"id":"4130607e-b687-45b2-a86e-9607a3bb9ee6","type":"LinearAxis"},{"id":"954e20d3-a5ba-4df7-a0e6-40e6bb70fe53","type":"Grid"},{"id":"618e4fe0-06fb-4624-891f-07e7d3d7c9ab","type":"BoxAnnotation"},{"id":"da97bce8-f1cf-40df-bd3d-0bfb4d7427e3","type":"Legend"},{"id":"c2b27855-16a0-466e-bff8-52af1b1342b6","type":"GlyphRenderer"},{"id":"4420007d-769f-4db6-a3cb-0c6c18a0f3d9","type":"GlyphRenderer"},{"id":"54250996-2d48-47c6-a734-b6c345acc82a","type":"Title"}],"title":{"id":"87000631-a09a-461c-bf53-948cf9e2acf9","type":"Title"},"tool_events":{"id":"ab9dc9d1-8e7d-45fd-adff-d0d65a02c8fa","type":"ToolEvents"},"toolbar":{"id":"ccd61a6b-8de0-44f5-b0b5-dfc30d532e7e","type":"Toolbar"},"toolbar_location":null,"x_range":{"id":"caa68f54-c562-4cad-8614-dae40fbe354a","type":"DataRange1d"},"y_range":{"id":"ea587e60-89b0-4fb1-babf-51652049472c","type":"DataRange1d"}},"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"},{"attributes":{"data_source":{"id":"c78ad910-d6a7-40ca-a9a7-44b214e1be06","type":"ColumnDataSource"},"glyph":{"id":"040b41a0-d154-45fa-9230-a174ebf98b72","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"f1345f17-8a99-4ab9-a43a-ec2dea23342b","type":"Line"},"selection_glyph":null},"id":"c9426e74-3afd-45c1-8aa8-e385731b8da2","type":"GlyphRenderer"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[50,55,61,69,73,83,90,99,106,111,118,125,132,139,151,168,184,201,216,234,254,262,275,294,311,327,348,371,396,421,451,485,513,550,571,605,625,650,676,698,711,737,754,774,787,804,825,844,856,870,879,892,900,905,911,923,928,937,947,955,962,962,964,968,971,973,974,978,982,985,987,988,990,991,991,991,992,992,995,996,996,997,997,997,997,997,997,997,997,998,998,998,998,998,999,999,999,999,999,999,999,999,999,999,999,999,999,999,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000]}},"id":"736af824-90f9-4dd9-a727-89c44273d8dd","type":"ColumnDataSource"},{"attributes":{"label":{"value":"Susceptible"},"renderers":[{"id":"ab15b2c1-2506-4559-b296-0444a1a4df10","type":"GlyphRenderer"}]},"id":"909ac954-0acd-40b7-8797-da82af402b4a","type":"LegendItem"},{"attributes":{"line_color":{"value":"#aec7e8"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"485837af-4003-481d-9e3b-22c770c076ed","type":"Line"},{"attributes":{"line_color":{"value":"#aec7e8"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"6a4bbc61-a6f5-42be-a2db-6c558b638ad8","type":"Line"},{"attributes":{},"id":"7a8063d2-dabf-46ad-8785-5f6bddb10d22","type":"BasicTicker"},{"attributes":{},"id":"32184b0f-dd31-489e-af88-98ba58a2b8ac","type":"BasicTicker"},{"attributes":{"overlay":{"id":"2aa729d3-0267-4b47-9c86-ae38a1666c11","type":"BoxAnnotation"},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"1af75cd2-afd0-4bb2-ac55-afc6a5c2ca33","type":"BoxZoomTool"},{"attributes":{"data_source":{"id":"69763aeb-4994-4abc-8d63-c0d635a2c46f","type":"ColumnDataSource"},"glyph":{"id":"f6760ec5-ed90-4f6b-a389-b1c0f4f64f72","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"a64201dd-935d-4b32-8a41-369a6535647b","type":"Line"},"selection_glyph":null},"id":"ecd60fd7-a26c-444e-abf4-e6039d2ce966","type":"GlyphRenderer"},{"attributes":{"overlay":{"id":"618e4fe0-06fb-4624-891f-07e7d3d7c9ab","type":"BoxAnnotation"},"plot":{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"}},"id":"0bd57782-9b74-4a40-a68a-65721e6b21e9","type":"BoxZoomTool"},{"attributes":{"grid_line_alpha":{"value":0.5},"plot":{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"},"ticker":{"id":"7a8063d2-dabf-46ad-8785-5f6bddb10d22","type":"BasicTicker"}},"id":"fd80d3ed-6f86-403d-8c4b-5cfeb4a776c0","type":"Grid"},{"attributes":{"plot":{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"}},"id":"c0668b37-8b41-41f1-bd84-0872250d0fae","type":"SaveTool"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"bcb427c8-0e8f-4b43-b330-8a1aa310e43d","type":"Line"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[950,945,939,931,927,917,910,901,894,889,882,875,868,861,849,832,816,799,784,766,746,738,725,706,689,673,652,629,604,579,549,515,487,450,429,395,375,350,324,302,289,263,246,226,213,196,175,156,144,130,121,108,100,95,89,77,72,63,53,45,38,38,36,32,29,27,26,22,18,15,13,12,10,9,9,9,8,8,5,4,4,3,3,3,3,3,3,3,3,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}},"id":"69763aeb-4994-4abc-8d63-c0d635a2c46f","type":"ColumnDataSource"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"48376b2c-7869-4a12-a480-c577074066c2","type":"PanTool"},{"attributes":{"plot":{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"}},"id":"525835dd-eaf0-4fc1-a085-dfc8fd0d4e77","type":"WheelZoomTool"},{"attributes":{"label":{"value":"Susceptible"},"renderers":[{"id":"ad955bdd-ea9b-4711-a851-b915321b851f","type":"GlyphRenderer"}]},"id":"9b0465f4-9b51-42d5-b25f-bc6eef43f918","type":"LegendItem"},{"attributes":{"dimension":1,"grid_line_alpha":{"value":0.5},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"ticker":{"id":"32184b0f-dd31-489e-af88-98ba58a2b8ac","type":"BasicTicker"}},"id":"ce449e57-2c0e-4bcf-b58d-674abde975a9","type":"Grid"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[0,2,2,2,4,4,7,7,7,9,10,11,11,11,12,13,15,17,19,22,24,25,28,30,31,34,35,40,46,51,54,61,67,71,79,82,86,93,101,105,117,121,130,136,143,148,150,156,163,172,180,185,189,198,207,212,215,225,237,244,248,251,262,265,269,273,280,286,298,308,315,326,335,341,343,349,354,358,367,372,375,383,389,401,408,418,421,426,434,443,453,456,461,467,471,472,487,491,497,500,509,512,518,524,526,528,532,535,539,544,546,552,556,561,563,564,569,574,580,582,582,583,588,595,599,605,610,618,622,624,625,634,636,640,645,647,652,655,659,661,667,673,677,683,686,689,693,698,702,704,707,710,714,715,719,719,720,723,727,728,733,737,741,744,746,748,753,755,757,759,759,763,764,765,768,770,771,772,774,775,781,784,785,786,788,791,797,799,802,806,808,813,817,820,823,827,828,828,830,831]}},"id":"c78ad910-d6a7-40ca-a9a7-44b214e1be06","type":"ColumnDataSource"},{"attributes":{},"id":"8654eb6a-1e02-4506-b86a-bcd84e471080","type":"BasicTicker"},{"attributes":{"align":"center","plot":{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"},"text":"percentage infected: 0.3"},"id":"54250996-2d48-47c6-a734-b6c345acc82a","type":"Title"},{"attributes":{"axis_label":"#Nodes","formatter":{"id":"4d707cfb-90ba-4533-b076-a0f6b88bc0d7","type":"BasicTickFormatter"},"plot":{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"},"ticker":{"id":"97a659f8-738c-44bc-8bfe-10725d0daa4e","type":"BasicTicker"}},"id":"a29a44a2-0fb0-45ae-863e-f19bb23eb83a","type":"LinearAxis"},{"attributes":{},"id":"a85fcbfc-ce33-471d-b81c-9f3db5169de5","type":"BasicTickFormatter"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"32e36402-9f68-433e-b0c2-91c27c1456e0","type":"Line"},{"attributes":{},"id":"a4c444ea-afe2-42ff-934e-8221368e5123","type":"ToolEvents"},{"attributes":{"active_drag":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"48376b2c-7869-4a12-a480-c577074066c2","type":"PanTool"},{"id":"c6e3a379-610d-45d6-96b2-f732a2e94e6e","type":"WheelZoomTool"},{"id":"1af75cd2-afd0-4bb2-ac55-afc6a5c2ca33","type":"BoxZoomTool"},{"id":"70c0ee7e-500b-49a2-af4b-44a42dd82cda","type":"SaveTool"},{"id":"53498048-937f-435c-9e55-c246830e877b","type":"ResetTool"},{"id":"1ef72fa5-2382-4fc5-a70b-1c801cb7076d","type":"HelpTool"}]},"id":"fff415bf-dbc0-441a-a759-dc72f26c8b4f","type":"Toolbar"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[950,948,947,941,935,933,931,926,919,914,907,903,895,889,882,871,855,844,835,825,808,788,772,760,747,726,710,690,682,662,646,629,615,594,578,564,545,514,492,470,441,423,399,384,357,337,319,304,291,280,267,258,249,237,226,216,201,198,191,178,182,181,176,163,157,154,147,149,137,131,124,119,110,105,108,107,97,104,104,107,107,108,107,108,101,110,117,111,113,110,116,115,117,118,111,111,109,108,107,101,102,98,99,103,109,110,110,108,111,106,111,113,115,120,119,119,116,114,116,114,110,106,112,107,101,103,105,105,108,111,102,104,112,108,105,103,102,95,93,91,94,97,98,91,94,96,91,90,94,92,91,85,82,89,83,74,75,83,96,93,84,86,79,82,82,80,87,86,77,80,87,91,89,86,83,93,91,94,99,94,88,91,85,80,86,87,91,92,88,78,80,82,81,78,81,89,95,99,100,104]}},"id":"862aabc0-e84b-439d-a3c8-d5fe10fa0e90","type":"ColumnDataSource"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"de0f30d8-f393-47ea-95bd-2a8828bd3f36","type":"Line"},{"attributes":{"axis_label":"Iterations","formatter":{"id":"da6b7a3f-3cfd-4423-ae73-5afcd3f4f85e","type":"BasicTickFormatter"},"plot":{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"},"ticker":{"id":"06f31848-16c6-4c6d-a35b-88df247cacfd","type":"BasicTicker"}},"id":"38d28985-a4d0-420a-b16c-d05ad24ff24a","type":"LinearAxis"},{"attributes":{"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"}},"id":"1ef72fa5-2382-4fc5-a70b-1c801cb7076d","type":"HelpTool"},{"attributes":{"active_drag":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"7d89ad74-e3c7-47c4-b1d7-211465866df4","type":"PanTool"},{"id":"525835dd-eaf0-4fc1-a085-dfc8fd0d4e77","type":"WheelZoomTool"},{"id":"fbb31755-ea84-4ea9-b46f-c9c3d2a713cb","type":"BoxZoomTool"},{"id":"00e84a3b-1996-4796-bb08-90d166034084","type":"SaveTool"},{"id":"2a1874fb-5f1f-447d-87c9-7b306a3083c8","type":"ResetTool"},{"id":"34a99321-e6d3-41b7-9d1c-89f40ca4ed50","type":"HelpTool"}]},"id":"7db71631-a724-4e90-a2bc-7042a0cca896","type":"Toolbar"},{"attributes":{"callback":null,"column_names":["x","y"],"data":{"x":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199],"y":[50,52,53,59,65,67,69,74,81,86,93,97,105,111,118,129,145,156,165,175,192,212,228,240,253,274,290,310,318,338,354,371,385,406,422,436,455,486,508,530,559,577,601,616,643,663,681,696,709,720,733,742,751,763,774,784,799,802,809,822,818,819,824,837,843,846,853,851,863,869,876,881,890,895,892,893,903,896,896,893,893,892,893,892,899,890,883,889,887,890,884,885,883,882,889,889,891,892,893,899,898,902,901,897,891,890,890,892,889,894,889,887,885,880,881,881,884,886,884,886,890,894,888,893,899,897,895,895,892,889,898,896,888,892,895,897,898,905,907,909,906,903,902,909,906,904,909,910,906,908,909,915,918,911,917,926,925,917,904,907,916,914,921,918,918,920,913,914,923,920,913,909,911,914,917,907,909,906,901,906,912,909,915,920,914,913,909,908,912,922,920,918,919,922,919,911,905,901,900,896]}},"id":"0cee5f04-0cb8-42c6-a32b-9a3a5c4d9d67","type":"ColumnDataSource"},{"attributes":{"overlay":{"id":"b44affcc-934e-4418-b560-2c4f12c41205","type":"BoxAnnotation"},"plot":{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"}},"id":"4a5705cd-92f0-4fac-95c7-345feae188a2","type":"BoxZoomTool"},{"attributes":{"label":{"value":"Infected"},"renderers":[{"id":"4420007d-769f-4db6-a3cb-0c6c18a0f3d9","type":"GlyphRenderer"}]},"id":"4e0e023b-ea82-4a03-afdc-65314af23673","type":"LegendItem"},{"attributes":{},"id":"68707d39-0620-4576-9ced-7c8e9c8046db","type":"BasicTicker"},{"attributes":{"line_color":{"value":"#aec7e8"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"29b375e5-9439-47fb-b5ae-af6b5906b2c3","type":"Line"},{"attributes":{"active_drag":"auto","active_scroll":"auto","active_tap":"auto","tools":[{"id":"0cfa6c6c-b98b-4baa-b07b-b63804ba22fc","type":"PanTool"},{"id":"40397fa0-9069-4b25-8b6b-49a1f022e535","type":"WheelZoomTool"},{"id":"0bd57782-9b74-4a40-a68a-65721e6b21e9","type":"BoxZoomTool"},{"id":"d8cebb2c-fcc2-425e-9b5e-1b686f53bbf0","type":"SaveTool"},{"id":"e3858e3e-80ac-41d0-b4ca-d00cbdf60c02","type":"ResetTool"},{"id":"70c698ca-1c84-4677-981f-0e933efb7a2e","type":"HelpTool"}]},"id":"ccd61a6b-8de0-44f5-b0b5-dfc30d532e7e","type":"Toolbar"},{"attributes":{"overlay":{"id":"285373e3-c9bd-4926-b503-9bb5607195eb","type":"BoxAnnotation"},"plot":{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"}},"id":"fbb31755-ea84-4ea9-b46f-c9c3d2a713cb","type":"BoxZoomTool"},{"attributes":{"label":{"value":"Susceptible"},"renderers":[{"id":"c2b27855-16a0-466e-bff8-52af1b1342b6","type":"GlyphRenderer"}]},"id":"1bf92cab-4283-4000-be0e-4be39d8798bb","type":"LegendItem"},{"attributes":{"plot":{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"}},"id":"d8cebb2c-fcc2-425e-9b5e-1b686f53bbf0","type":"SaveTool"},{"attributes":{"data_source":{"id":"736af824-90f9-4dd9-a727-89c44273d8dd","type":"ColumnDataSource"},"glyph":{"id":"6a4bbc61-a6f5-42be-a2db-6c558b638ad8","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"bcb427c8-0e8f-4b43-b330-8a1aa310e43d","type":"Line"},"selection_glyph":null},"id":"fa1dc348-ba35-4d96-abb3-8ea86458175d","type":"GlyphRenderer"},{"attributes":{"plot":{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"}},"id":"d4b743be-890a-46f6-9893-d8ffa12ece44","type":"HelpTool"},{"attributes":{},"id":"aa409463-913d-4b55-962c-c43f408135f0","type":"BasicTickFormatter"},{"attributes":{},"id":"098eff25-f41e-40b4-9aca-f1206151a05b","type":"BasicTickFormatter"},{"attributes":{"plot":{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"}},"id":"2a1874fb-5f1f-447d-87c9-7b306a3083c8","type":"ResetTool"},{"attributes":{"plot":null,"text":"SI - Diffusion Trend"},"id":"f1681181-4529-4e0a-9f01-1d2d13ba83b6","type":"Title"},{"attributes":{"plot":{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"}},"id":"e3858e3e-80ac-41d0-b4ca-d00cbdf60c02","type":"ResetTool"},{"attributes":{"dimension":1,"grid_line_alpha":{"value":0.5},"plot":{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"},"ticker":{"id":"7c9995a4-51f7-4614-abc4-d134be4cbcec","type":"BasicTicker"}},"id":"954e20d3-a5ba-4df7-a0e6-40e6bb70fe53","type":"Grid"},{"attributes":{"axis_label":"Iterations","formatter":{"id":"aa409463-913d-4b55-962c-c43f408135f0","type":"BasicTickFormatter"},"plot":{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"},"ticker":{"id":"68707d39-0620-4576-9ced-7c8e9c8046db","type":"BasicTicker"}},"id":"a9cc4998-4710-4b0d-8768-831b6ad8fa1e","type":"LinearAxis"},{"attributes":{"grid_line_alpha":{"value":0.5},"plot":{"id":"fd341b13-e3d0-4c0f-9242-e7e36bd057da","subtype":"Figure","type":"Plot"},"ticker":{"id":"06f31848-16c6-4c6d-a35b-88df247cacfd","type":"BasicTicker"}},"id":"0a13ea5e-5ba2-484a-b808-b8fbfecfebc8","type":"Grid"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"84ab2ba5-6516-497c-9b73-1fbd79ff8604","type":"Line"},{"attributes":{"label":{"value":"Removed"},"renderers":[{"id":"c9426e74-3afd-45c1-8aa8-e385731b8da2","type":"GlyphRenderer"}]},"id":"bd422dde-b71e-4c36-b31d-80b27c2abe2c","type":"LegendItem"},{"attributes":{"align":"center","plot":{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"},"text":"percentage infected: 0.05, beta: 0.001, lambda: 0.01"},"id":"cb412e46-b85a-4a8e-8bfd-a8e13b284339","type":"Title"},{"attributes":{},"id":"da6b7a3f-3cfd-4423-ae73-5afcd3f4f85e","type":"BasicTickFormatter"},{"attributes":{"bottom_units":"screen","fill_alpha":{"value":0.5},"fill_color":{"value":"lightgrey"},"left_units":"screen","level":"overlay","line_alpha":{"value":1.0},"line_color":{"value":"black"},"line_dash":[4,4],"line_width":{"value":2},"plot":null,"render_mode":"css","right_units":"screen","top_units":"screen"},"id":"285373e3-c9bd-4926-b503-9bb5607195eb","type":"BoxAnnotation"},{"attributes":{"label":{"value":"Infected"},"renderers":[{"id":"2f291fbf-aa58-403b-9656-c032207caf75","type":"GlyphRenderer"}]},"id":"996c6dba-dc48-489d-8445-a83ce75ea7b5","type":"LegendItem"},{"attributes":{"callback":null},"id":"b035140b-eb4e-4e76-bb04-021785201d9e","type":"DataRange1d"},{"attributes":{"axis_label":"Iterations","formatter":{"id":"84ebdd3d-7723-4683-8092-1ba79733178d","type":"BasicTickFormatter"},"plot":{"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"},"ticker":{"id":"7a8063d2-dabf-46ad-8785-5f6bddb10d22","type":"BasicTicker"}},"id":"686cc740-de4d-4590-8e1b-0604afcf0f1d","type":"LinearAxis"},{"attributes":{"line_alpha":{"value":0.1},"line_color":{"value":"#1f77b4"},"line_width":{"value":2},"x":{"field":"x"},"y":{"field":"y"}},"id":"a64201dd-935d-4b32-8a41-369a6535647b","type":"Line"},{"attributes":{"data_source":{"id":"98a08cf6-efd8-4cd0-b2c3-6d40d2cde539","type":"ColumnDataSource"},"glyph":{"id":"a4961edf-730d-4b8d-9ac3-8507bb29d046","type":"Line"},"hover_glyph":null,"nonselection_glyph":{"id":"2433a5a8-f98c-4771-8aeb-b952443305a7","type":"Line"},"selection_glyph":null},"id":"4420007d-769f-4db6-a3cb-0c6c18a0f3d9","type":"GlyphRenderer"},{"attributes":{"callback":null},"id":"314e9b9d-09c4-426b-a260-7aa88578698f","type":"DataRange1d"},{"attributes":{"below":[{"id":"686cc740-de4d-4590-8e1b-0604afcf0f1d","type":"LinearAxis"},{"id":"b8c7de88-eb27-44d7-8f92-9952fdef32bc","type":"Title"}],"left":[{"id":"417d9953-84bf-4966-b3d4-924fbf4758cb","type":"LinearAxis"}],"plot_height":400,"plot_width":400,"renderers":[{"id":"686cc740-de4d-4590-8e1b-0604afcf0f1d","type":"LinearAxis"},{"id":"fd80d3ed-6f86-403d-8c4b-5cfeb4a776c0","type":"Grid"},{"id":"417d9953-84bf-4966-b3d4-924fbf4758cb","type":"LinearAxis"},{"id":"5a71e431-4f7e-411a-810e-664860fc9aa8","type":"Grid"},{"id":"b44affcc-934e-4418-b560-2c4f12c41205","type":"BoxAnnotation"},{"id":"61acbbd4-1485-4f99-a066-1d8f4285fb7e","type":"Legend"},{"id":"ecd60fd7-a26c-444e-abf4-e6039d2ce966","type":"GlyphRenderer"},{"id":"fa1dc348-ba35-4d96-abb3-8ea86458175d","type":"GlyphRenderer"},{"id":"b8c7de88-eb27-44d7-8f92-9952fdef32bc","type":"Title"}],"title":{"id":"f1681181-4529-4e0a-9f01-1d2d13ba83b6","type":"Title"},"tool_events":{"id":"9f2cbfb1-f808-43bc-83bb-09c0274e6c89","type":"ToolEvents"},"toolbar":{"id":"a0fec24f-65f5-4aec-a161-62cb579dc496","type":"Toolbar"},"toolbar_location":null,"x_range":{"id":"9dabb2ef-f9e4-419b-a3ba-e85ee9c7312a","type":"DataRange1d"},"y_range":{"id":"f09408a8-5aa9-443c-ac55-134c4f66ea87","type":"DataRange1d"}},"id":"527b6e85-a7a5-4ab0-b608-8076f95dfa46","subtype":"Figure","type":"Plot"},{"attributes":{},"id":"7c9995a4-51f7-4614-abc4-d134be4cbcec","type":"BasicTicker"},{"attributes":{"items":[{"id":"9b0465f4-9b51-42d5-b25f-bc6eef43f918","type":"LegendItem"},{"id":"49032db6-b202-4ecb-b8d0-2742b244630a","type":"LegendItem"}],"orientation":"horizontal","plot":{"id":"584cdd63-7e0f-48a3-bd64-7d64579cae7c","subtype":"Figure","type":"Plot"}},"id":"73373dd3-d3da-4db4-a02c-2b542baae787","type":"Legend"},{"attributes":{"axis_label":"Iterations","formatter":{"id":"098eff25-f41e-40b4-9aca-f1206151a05b","type":"BasicTickFormatter"},"plot":{"id":"9391ef7c-0136-4870-a9cc-cac314cebfe9","subtype":"Figure","type":"Plot"},"ticker":{"id":"8654eb6a-1e02-4506-b86a-bcd84e471080","type":"BasicTicker"}},"id":"39ccff6f-cdcf-4ddb-a0b5-fa52ad5425f5","type":"LinearAxis"}],"root_ids":["df321518-6e67-4286-b70a-a05e23a97a5e"]},"title":"Bokeh Application","version":"0.12.4"}};
                var render_items = [{"docid":"36bb618b-1d3c-4ebf-a033-48c469ebc39a","elementid":"d4504979-9a6d-4461-ae24-75391fedd712","modelid":"df321518-6e67-4286-b70a-a05e23a97a5e"}];
                
                Bokeh.embed.embed_items(docs_json, render_items);
              };
              if (document.readyState != "loading") fn();
              else document.addEventListener("DOMContentLoaded", fn);
            })();
          },
          function(Bokeh) {
          }
        ];
      
        function run_inline_js() {
          
          if ((window.Bokeh !== undefined) || (force === true)) {
            for (var i = 0; i < inline_js.length; i++) {
              inline_js[i](window.Bokeh);
            }if (force === true) {
              display_loaded();
            }} else if (Date.now() < window._bokeh_timeout) {
            setTimeout(run_inline_js, 100);
          } else if (!window._bokeh_failed_load) {
            console.log("Bokeh: BokehJS failed to load within specified timeout.");
            window._bokeh_failed_load = true;
          } else if (force !== true) {
            var cell = $(document.getElementById("d4504979-9a6d-4461-ae24-75391fedd712")).parents('.cell').data().cell;
            cell.output_area.append_execute_result(NB_LOAD_WARNING)
          }
      
        }
      
        if (window._bokeh_is_loading === 0) {
          console.log("Bokeh: BokehJS loaded, going straight to plotting");
          run_inline_js();
        } else {
          load_libs(js_urls, function() {
            console.log("Bokeh: BokehJS plotting callback run at", now());
            run_inline_js();
          });
        }
      }(this));
    </script>



