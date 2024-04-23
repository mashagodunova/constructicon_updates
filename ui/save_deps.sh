# links
declare -a arr=(
  "https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"
  "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"
  "https://cdn.jsdelivr.net/npm/@riophae/vue-treeselect@^0.4.0/dist/vue-treeselect.min.css"
)

for i in "${arr[@]}"
do
   wget -nc "$i" -O ./static/css/$(basename "$i") -q
   echo "<link rel=\"stylesheet\" href=\"/static/css/$(basename "$i")\" />"
done

echo

# scripts
declare -a arr=(
  "https://cdn.jsdelivr.net/npm/vue@2.6.11/dist/vue.min.js"
  "https://cdn.jsdelivr.net/npm/@riophae/vue-treeselect@^0.4.0/dist/vue-treeselect.umd.min.js"
  "https://cdn.jsdelivr.net/npm/js-yaml@3.14.0/dist/js-yaml.min.js"
  "https://cdn.jsdelivr.net/npm/axios@0.19.2/dist/axios.min.js"
  "https://cdn.jsdelivr.net/npm/lodash@4.17.19/lodash.min.js"
  "https://cdn.jsdelivr.net/npm/js-search@2.0.0/dist/umd/js-search.min.js"
  "https://cdn.jsdelivr.net/npm/chart.js@3.7.0/dist/chart.min.js"
  "https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-datalabels/2.0.0-rc.1/chartjs-plugin-datalabels.min.js"
  "https://d3js.org/d3.v7.min.js"
  "https://code.jquery.com/jquery-3.5.1.slim.min.js"
  "https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js"
  "https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js"
  "https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/js/bootstrap.bundle.min.js"
)

for i in "${arr[@]}"
do
   wget -nc "$i" -O ./static/static/js/$(basename "$i") -q
   echo "<script src=\"/static/js/$(basename "$i")\" defer></script>"
done
