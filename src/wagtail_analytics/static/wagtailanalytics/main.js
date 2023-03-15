function getReport(reportUrl) {
  fetch(`${reportUrl}`)
    .then((response) => response.json())
    .then((report) => {
      console.log(report);
      renderSessions("sessions-container", report);
      renderTopPages("top-pages-container", report["top_pages"]);
      renderTopReferrers("top-referrers-container", report["top_sources"]);
      return true;
    })
    .catch(function (error) {
      console.log("Request failed", error);
      return false;
    });
}

function makeCanvas(container) {
  var container = document.getElementById("sessions-container");
  var canvas = document.createElement("canvas");
  var ctx = canvas.getContext("2d");

  container.innerHTML = "";
  canvas.width = container.offsetWidth;
  canvas.height = container.offsetHeight;
  container.appendChild(canvas);

  return ctx;
}

function renderSessions(container, report) {
  this_week_integers = [];
  last_week_integers = [];

  for (var i = 0; i < report["visitors_this_week"].length; i++) {
    this_week_integers.push(parseInt(report["visitors_this_week"][i][1]));
    last_week_integers.push(parseInt(report["visitors_last_week"][i][1]));
  }
  var labels = report["visitors_this_week"].map((value) => value[0]);
  var data = {
    labels,
    datasets: [
      {
        label: "Last Week",
        backgroundColor: "rgba(252,242,242,0.5)",
        borderColor: "rgba(252,242,242,1)",
        data: last_week_integers,
      },
      {
        label: "This Week",
        backgroundColor: "rgba(243,126,119,0.5)",
        borderColor: "rgba(243,126,119,1)",
        data: this_week_integers,
      },
    ],
  };

  var config = {
    type: "line",
    data: data,
    options: {
      responsive: true,
    },
  };

  new Chart(makeCanvas(container), config);
}

function renderTopPages(container, report) {
  var html = "";
  for (var i = 0; i < report.length; i++) {
    html +=
      "<tr><td>" +
      report[i]["url"] +
      "</td><td>" +
      report[i]["pageviews"] +
      "</td></tr>";
  }

  document.getElementById(container).innerHTML = html;
}

function renderTopReferrers(container, report) {
  var html = "";
  for (var i = 0; i < report.length; i++) {
    html +=
      "<tr><td>" +
      report[i]["name"] +
      "</td><td>" +
      report[i]["pageviews"] +
      "</td></tr>";
  }

  document.getElementById(container).innerHTML = html;
}
