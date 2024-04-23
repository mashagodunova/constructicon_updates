// with this we make js less forgiving so that we catch
// more hidden errors during development
'use strict';

const REMOTE_URL = 'https://constructicon.ruscorpora.ru';
// const REMOTE_URL = 'http://localhost:8080';

// https://stackoverflow.com/a/196991
function to_title_case(str) {
    return str.replace(
        /\w\S*/g,
        function(txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        }
    );
}

var groupBy = function(xs, key) {
  return xs.reduce(function(rv, x) {
    (rv[x[key]] = rv[x[key]] || []).push(x);
    return rv;
  }, {});
};

function groupSemanticTypes(lst) {
  let res = {};
  for (let elt of lst) {
    res[elt.id] = { ...elt, children: [] };
  }
  res[null] = { children: [] };
  for (let elt of lst) {
    res[elt.parent_id].children.push(res[elt.id]);
  }
  return res[null].children;
}

/*
function build_search_index(record_numbers, records, keys) {
    let search_index = new JsSearch.Search('record');
    // https://github.com/bvaughn/js-search#configuring-the-index-strategy
    search_index.indexStrategy = new JsSearch.AllSubstringsIndexStrategy();
    for (let key of keys) {
        search_index.addIndex(key);
    }
    for (let record_number of record_numbers) {
        search_index.addDocuments([records[record_number]]);
    }
    return search_index;
}
*/

function collect_options(options) {
    return options.map((e) => ({id: e.id, label: e.name, ...e}));
}


function object_is_empty(obj) {
    for (let key in obj) {
        if (obj.hasOwnProperty(key))
            return false;
    }
    return true;
}


// translates array to list of items
function _helper(array) {
    let tree = [];

    let keys = [];
    for (let prop in array) {
        keys.push(prop);
    }
    keys.sort();

    for (let prop of keys) {
        if (Object.prototype.hasOwnProperty.call(array, prop)) {
            if (object_is_empty(prop)) {
                tree.push({
                    id: prop,
                    label: prop,
                });
            } else {
                tree.push({
                    id: prop,
                    label: prop,
                    children: _helper(array[prop]),
                });
            }
        }
    }

    return tree;
}


/*
function collect_options_tree(record_numbers, records, key) {
    // first we build up a simpler array tree from all entries
    let tree_array = {};
    for (let record_number of record_numbers) {
        if (records[record_number][key] != null) {
            for (let element_0 of records[record_number][key]) {
                let type_0 = element_0["type"];
                if (!(type_0 in tree_array)) {
                    tree_array[type_0] = {};
                }
                if ("subtypes" in element_0) {
                    for (let element_1 of element_0["subtypes"]) {
                        let type_1 = element_1["type"];
                        if (!(type_1 in tree_array[type_0])) {
                            tree_array[type_0][type_1] = {};
                        }
                        if ("subtypes" in element_1) {
                            for (let element_2 of element_1["subtypes"]) {
                                let type_2 = element_2["type"];
                                if (!(type_2 in tree_array[type_0][type_1])) {
                                    tree_array[type_0][type_1][type_2] = {};
                                }
                                if ("subtypes" in element_2) {
                                    for (let element_3 of element_2["subtypes"]) {
                                        let type_3 = element_3["type"];
                                        if (!(type_3 in tree_array[type_0][type_1][type_2])) {
                                            tree_array[type_0][type_1][type_2][type_3] = {};
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // in the second step we translate this to a structure required by https://vue-treeselect.js.org/
    let tree = _helper(tree_array);

    return tree;
}
*/

/*
function flatten_semantic_types(record_numbers, records) {
    let key = "semantic_types";

    // FIXME: this traversal is similar to function above
    for (let record_number of record_numbers) {
        let flattened_list = [];
        if (records[record_number][key] != null) {
            for (let element_0 of records[record_number][key]) {
                let type_0 = element_0["type"];
                flattened_list.push(type_0);
                if ("subtypes" in element_0) {
                    for (let element_1 of element_0["subtypes"]) {
                        let type_1 = element_1["type"];
                        flattened_list.push(type_1);
                        if ("subtypes" in element_1) {
                            for (let element_2 of element_1["subtypes"]) {
                                let type_2 = element_2["type"];
                                flattened_list.push(type_2);
                                if ("subtypes" in element_2) {
                                    for (let element_3 of element_2["subtypes"]) {
                                        let type_3 = element_3["type"];
                                        flattened_list.push(type_3);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        records[record_number]["semantic_types_flat"] = flattened_list;
    }

    return records;
}
*/

// from https://stackoverflow.com/a/48969580
function makeRequest(method, url) {
    return new Promise(function (resolve, reject) {
        let xhr = new XMLHttpRequest();
        xhr.open(method, url);
        xhr.onload = function () {
            if (this.status >= 200 && this.status < 300) {
                resolve(xhr.response);
            } else {
                reject({
                    status: this.status,
                    statusText: xhr.statusText
                });
            }
        };
        xhr.onerror = function () {
            reject({
                status: this.status,
                statusText: xhr.statusText
            });
        };
        xhr.send();
    });
}


async function fetch_data(data, url_prefix) {
    let result = await makeRequest("GET", url_prefix + '?offset=0&limit=100&random_sort=false');
    let json_data = JSON.parse(result);

    data.records = json_data.items;
    data.records_number = json_data.total;
    /*
    let records = {};
    let record_numbers = [];
    let levels = new Set();

    for (let key of Object.keys(json_data)) {
        records[key] = json_data[key];
        records[key].record = key;
        record_numbers.push(key);
        levels.add(json_data[key].cefr_level);
    }

    data.records = records;
    data.record_numbers = record_numbers;

    data.levels = Array.from(levels);
    data.levels.sort();
    */

    let search_options = await makeRequest("GET", REMOTE_URL + '/api/construction/search_info/');
    search_options = JSON.parse(search_options);

    const raw = collect_options(search_options.semantic_types);
    let s = groupBy(raw, 'parent_id');
    raw.forEach((e) => {
        const subtypes = s[e.id];
        if (subtypes !== undefined) {
            e['children'] = subtypes;
        }
    });
    data.semantic_types_options = s[null];

    // data.semantic_types_options = collect_options(search_options.semantic_types);
    data.semantic_roles_options = collect_options(search_options.semantic_roles);
    data.morphology_options = collect_options(search_options.morphological_tags);
    data.syntactic_type_of_construction_options = collect_options(search_options.syntactic_types);
    data.syntactic_function_of_anchor_options = collect_options(search_options.syntactic_functions);
    data.syntactic_structure_of_anchor_options = collect_options(search_options.syntactic_structures);
    data.part_of_speech_of_anchor_options = collect_options(search_options.anchor_poss);
    data.level_options = [{id: 'A1', label: 'A1'}, {id: 'A2', label: 'A2'}, {id: 'B1', label: 'B1'},
                            {id: 'B2', label: 'B2'}, {id: 'C1', label: 'C1'}, {id: 'C2', label: 'C2'}];
    data.glosses_options =  collect_options(search_options.morphological_tags);

    // data.semantic_types_options = collect_options_tree(data.record_numbers, data.records, 'semantic_types');

    // we need to flatten the semantic types tree for the search index
    // for some reason it does not pick up the options otherwise
    /*
    data.records = flatten_semantic_types(data.record_numbers, data.records);

    data.search_index = {};
    for (let key of ['name',
            'illustration',
            'semantic_roles',
            'morphology',
            'syntactic_type_of_construction',
            'syntactic_function_of_anchor',
            'syntactic_structure_of_anchor',
            'part_of_speech_of_anchor',
            'cefr_level',
            'semantic_types_flat',
            'semantic_types',
	    'glosses',
        ]) {
        data.search_index[key] = build_search_index(data.record_numbers, data.records, [key]);
    }
    */

    data.all_data_loaded = true;
    data.show_data_spinner = false;
}


// based on https://stackoverflow.com/a/19270021 (CC-BY-SA 3.0)
function random_selection(arr, n_max) {
    let len = arr.length;
    let n = Math.min(n_max, len);
    let result = new Array(n);
    let taken = new Array(len);
    while (n--) {
        let x = Math.floor(Math.random() * len);
        result[n] = arr[x in taken ? taken[x] : x];
        taken[x] = --len in taken ? taken[len] : len;
    }
    return result;
}


Vue.component('treeselect', VueTreeselect.Treeselect);


var app = new Vue({
    el: '#app',
    delimiters: ['{[', ']}'],
    data: {
        // search_index: null,
        show_additional_information: false,
        show_data_spinner: true,
        all_data_loaded: false,
        current_record_number: null,
        currentRoute: window.location.pathname,
        globNumber: localStorage.getItem('globNumber') || null,
        globId: localStorage.getItem('globId') || null,
        copied: false,
        records_number: 0,
        records: [],
        daily_dose_level: 'A1',
        search_string: '',
        levels: [],
        semantic_roles_options: [],
        semantic_roles_selected: null,
        morphology_options: [],
        morphology_selected: null,
        syntactic_type_of_construction_options: [],
        syntactic_type_of_construction_selected: null,
        syntactic_function_of_anchor_options: [],
        syntactic_function_of_anchor_selected: null,
        syntactic_structure_of_anchor_options: [],
        syntactic_structure_of_anchor_selected: null,
        part_of_speech_of_anchor_options: [],
        part_of_speech_of_anchor_selected: null,
        level_options: [],
        level_selected: null,
        semantic_types_options: [],
        semantic_types_selected: null,
        glosses_options:{},
        glosses_selected:null,
        random_records: [],
        searchType: 'text'
    },
    created: function() {
        this.show_data_spinner = true;

        fetch_data(this, REMOTE_URL + '/api/construction/');

        // https://lodash.com/docs#debounce
        this.search_debounced = _.debounce(this.search, 500);
        this.advanced_search_debounced = _.debounce(this.advanced_search, 500);
        this.checkRoute();
    },
    watch: {
        all_data_loaded: function(new_, old_) {
            // to make sure that when we load the page first time, we see all results
            this.search();
        },
        search_string: function(new_, old_) {
            this.search_debounced();
        },
        semantic_types: function(new_, old_) {
            this.advanced_search_debounced();
        },
        semantic_roles_selected: function(new_, old_) {
            this.advanced_search_debounced();
        },
        morphology_selected: function(new_, old_) {
            this.advanced_search_debounced();
        },
        syntactic_type_of_construction_selected: function(new_, old_) {
            this.advanced_search_debounced();
        },
        syntactic_function_of_anchor_selected: function(new_, old_) {
            this.advanced_search_debounced();
        },
        syntactic_structure_of_anchor_selected: function(new_, old_) {
            this.advanced_search_debounced();
        },
        part_of_speech_of_anchor_selected: function(new_, old_) {
            this.advanced_search_debounced();
        },
        level_selected: function(new_, old_) {
            this.advanced_search_debounced();
        },
        semantic_types_selected: function(new_, old_) {
            this.advanced_search_debounced();
        },
	glosses_selected: function(new_, old_) {
            this.advanced_search_debounced();
        },
    },
    methods: {
        checkRoute() {
            const regex_url1 = /construction\/\d+/;
            // const regex_url2 = /construction\/id=\d+/;

            if (regex_url1.test(this.currentRoute)) {
                var index = parseInt(this.currentRoute.split('/construction/')[1]);
                localStorage.setItem('globId', index);
                window.location.href = '/construction/';
                return;
            }

          }, 
        // for x={'this': 'that'} returns 'this'
        key: function(x) {
            return Object.keys(x)[0];
        },
        // for x={'this': 'that'} returns 'that'
        value: function(x) {
            return x[Object.keys(x)[0]];
        },

	/*redirectToRecord: function(recordId) {

    window.location.href = 'http://127.0.0.1:3000/construction/'+ recordId;
  },*/
search: function() {
            // let record_numbers_matching_search = [];

            if (false) { // this.search_string == '') {
                // record_numbers_matching_search = this.record_numbers;
            } else { 
             let url = REMOTE_URL + '/api/construction/?offset=0&limit=200&' + this.searchType + '=' + this.search_string;
                var xhr = new XMLHttpRequest();
                xhr.open('GET', url, false)
                xhr.send();
                if (xhr.status != 200) {
                    // error handling
                    console.log( xhr.status + ': ' + xhr.statusText ); // example output: 404: Not Found
                } else {
                    // output results
                    let data = JSON.parse(xhr.responseText);
                    this.records_number = data.total;
                    this.records = data.items;
                    localStorage.setItem('globRecords', data.items);
                    /*
                    for(let key of JSON.parse(xhr.responseText).items){
                        record_numbers_matching_search.push(key['id'].toString())
                    }
                    */
                }
            }
        },
        advanced_search: function() {
            let selected_options = {};
            selected_options['semantic_types'] = this.semantic_types_selected;
            selected_options['semantic_roles'] = this.semantic_roles_selected;
            selected_options['morphological_tags'] = this.morphology_selected;
            selected_options['syntactic_types'] = this.syntactic_type_of_construction_selected;
            selected_options['syntactic_function'] = this.syntactic_function_of_anchor_selected;
            selected_options['syntactic_structures'] = this.syntactic_structure_of_anchor_selected;
            selected_options['part_of_speech_of_anchor'] = this.part_of_speech_of_anchor_selected;
            selected_options['cefr_level'] = this.level_selected;
            selected_options['semantic_types'] = this.semantic_types_selected;
	    selected_options['glosses'] = this.glosses_selected;
            let url = REMOTE_URL + '/api/construction/?offset=0&limit=300&random_sort=false'

            for (let key of [
                    'cefr_level',
                    'syntactic_types',
                    'semantic_types',
                    'syntactic_function',
                    'syntactic_structures',
                    'morphological_tags',
                    'semantic_roles',
                    'part_of_speech_of_anchor',
		   'glosses'
            ]) {
                if (selected_options[key] != null) {
                    let search_string = selected_options[key].join(',');
                    url = url + '&' + key + '=' + search_string;
                    console.log(url)
                }
            }

            var xhr = new XMLHttpRequest();
            xhr.open('GET', url, false)
            xhr.send();
            if (xhr.status != 200) {
                // error handling
                console.log( xhr.status + ': ' + xhr.statusText ); // example output: 404: Not Found
            } else {
                // output results
                let data = JSON.parse(xhr.responseText);
                this.records_number = data.total;
                this.records = data.items;

                /*
                for(let key of JSON.parse(xhr.responseText).items){
                    record_numbers_matching_search.push(key['id'].toString())
                }
                */
            }
            // console.log(record_numbers_matching_search)
        },
        annotate: function(text) {
            // renders words that come right after [...] as subscript with color
            let matches = text.match(/(?<=\])[A-Za-z]+/g);
            if (matches){
                for (let substring of matches) {
                    text = text.replace(substring, '<sub><span style="color: #db2f6d">' + substring + '</span></sub>');
                }
            }
            return text;
        },
        globIdUpdate: function(x, data) {
            if (x != null){
                this.globNumber = x;
                this.globId = this.records[x].id;
                this.records = data;
                localStorage.setItem('globNumber', this.globNumber); 
                localStorage.setItem('globId', this.globId); 
            }
        },
        parse_lists: function(text) {
            return text.split(", ");
        },
        parse_dependency_structures: function(text) {
            return text.split("+");
        },
        get_random_selection: function() {
            let records_with_this_level = [];

            // for (let record_number of this.record_numbers) {
            //     if (this.records[record_number].cefr_level == this.daily_dose_level) {
            //         records_with_this_level.push(record_number);
            //     }
            // }
            // let selected = random_selection(records_with_this_level, 5);
            // selected.sort((a, b) => a - b);
            // this.record_numbers_matching_search = selected;
            // console.log(selected)

            var xhr = new XMLHttpRequest();

            var level_query = REMOTE_URL + '/api/construction/?offset=0&limit=5&random_sort=true&cefr_level=' + this.daily_dose_level
            xhr.open('GET', level_query, false)
            xhr.send();

            if (xhr.status != 200) {
                console.log( xhr.status + ': ' + xhr.statusText );
            } else {
                let records_with_this_level = JSON.parse(xhr.responseText).items;
                // let selected = records_with_this_level.slice(0, 5)
                // this.record_numbers_matching_search = selected;
                // this.random_records = selected
                // console.log(selected);
                this.records = records_with_this_level;
            }
        },
        get_full_tags: function(text){
            var dict = {
                "c": "Colloquial",
                "f": "Formal",
                "o": "Obsolete",
                "n": "",
                "i": "Interrogative",
                "d": "Declarative",
                "e": "Exclamatory",
                "ie": "Interrogative exclamatory",
                "na": ""
            }
            return dict[text]
        }

    }
})
