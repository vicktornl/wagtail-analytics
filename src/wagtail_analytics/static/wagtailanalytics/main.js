function query(params) {
  return new Promise(function(resolve, reject) {
    var data = new gapi.analytics.report.Data({
      query: params
    });
    data
      .once("success", function(response) {
        resolve(response);
      })
      .once("error", function(response) {
        reject(response);
      })
      .execute();
  });
}

function makeCanvas(id) {
  var container = document.getElementById(id);
  var canvas = document.createElement("canvas");
  var ctx = canvas.getContext("2d");

  container.innerHTML = "";
  canvas.width = container.offsetWidth;
  canvas.height = container.offsetHeight;
  container.appendChild(canvas);

  return ctx;
}

function renderSessions(id, container) {
  var now = moment();

  var thisWeek = query({
    ids: "ga:" + id,
    dimensions: "ga:date,ga:nthDay",
    metrics: "ga:sessions",
    "start-date": moment(now).subtract(1, "day").day(0).format("YYYY-MM-DD"),
    "end-date": moment(now).format("YYYY-MM-DD"),
  });

  var lastWeek = query({
    ids: "ga:" + id,
    dimensions: "ga:date,ga:nthDay",
    metrics: "ga:sessions",
    "start-date": moment(now)
      .subtract(1, "day")
      .day(0)
      .subtract(1, "week")
      .format("YYYY-MM-DD"),
    "end-date": moment(now)
      .subtract(1, "day")
      .day(6)
      .subtract(1, "week")
      .format("YYYY-MM-DD"),
  });

  Promise.all([thisWeek, lastWeek]).then(function(results) {
    var data1 = results[0].rows.map(function(row) {
      return +row[2];
    });
    var data2 = results[1].rows.map(function(row) {
      return +row[2];
    });
    var labels = results[1].rows.map(function(row) {
      return +row[0];
    });

    labels = labels.map(function(label) {
      return moment(label, "YYYYMMDD").format("ddd");
    });

    var data = {
      labels: labels,
      datasets: [{
        label: "Last Week",
        backgroundColor: "rgba(252,242,242,0.5)",
        borderColor: "rgba(252,242,242,1)",
        data: data2,
      }, {
        label: "This Week",
        backgroundColor: "rgba(243,126,119,0.5)",
        borderColor: "rgba(243,126,119,1)",
        data: data1,
      }, ],
    };

    var config = {
      type: "line",
      data: data,
      options: {
        responsive: true,
      },
    };

    new Chart(makeCanvas(container), config);
  });
}

function renderTopPages(id, container) {
  var now = moment();

  var last30Days = query({
    ids: "ga:" + id,
    dimensions: "ga:hostname,ga:pagePath",
    metrics: "ga:pageviews",
    "start-date": moment(now).subtract(30, "days").format("YYYY-MM-DD"),
    "end-date": moment(now).format("YYYY-MM-DD"),
    sort: "-ga:pageviews",
    "max-results": 10,
  });

  Promise.all([last30Days]).then(function(results) {
    var data = results[0].rows.map(function(row) {
      return row;
    });

    var html = "";

    for (var i = 0; i < data.length; i++) {
      html += "<tr><td>" + data[i][1] + "</td><td>" + data[i][2] + "</td></tr>";
    }

    document.getElementById(container).innerHTML = html;
  });
}

function renderTopReferrers(id, container) {
  var now = moment();

  var last30Days = query({
    ids: "ga:" + id,
    dimensions: "ga:fullReferrer",
    metrics: "ga:pageviews",
    "start-date": moment(now).subtract(30, "days").format("YYYY-MM-DD"),
    "end-date": moment(now).format("YYYY-MM-DD"),
    sort: "-ga:pageviews",
    "max-results": 10,
  });

  Promise.all([last30Days]).then(function(results) {
    var data = results[0].rows.map(function(row) {
      return row;
    });

    var html = "";

    for (var i = 0; i < data.length; i++) {
      html += "<tr><td>" + data[i][0] + "</td><td>" + data[i][1] + "</td></tr>";
    }

    document.getElementById(container).innerHTML = html;
  });
}


function getAPIToken(url) {
  return new Promise(function(resolve, reject) {
    var request = new XMLHttpRequest();
    request.open("GET", url);

    request.onload = function() {
      if (request.readyState === request.DONE) {
        if (request.status === 200) {
          data = JSON.parse(request.response)
          resolve(data["access_token"])
        }
      }
    }
    request.send()
  });
}

function getPageID() {
  element = document.getElementById("page-edit-form").action;
  var element_arr = element.split("/");
  var lastTwo = element_arr.slice(-3);
  var res = lastTwo[0];
  return res;
}
