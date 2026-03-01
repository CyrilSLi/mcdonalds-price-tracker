function substituteLocationString(location) {
    [...document.getElementsByClassName("location-substitute")].forEach(el => {
        if (el.href) {
            el.href = el.href.replace("%location%", location);
        } else {
            el.textContent = el.textContent.replace("%location%", location);
        }
    });
}

const params = new URLSearchParams(window.location.search);
if (!params.has("location")) {
    substituteLocationString("");
    (async () => {
        const addresses = await fetch("addresses.json").then(res => res.json());
        document.getElementById("locations").innerHTML += addresses.__locations__.map(loc => {
            return `<a href="?location=${loc}"><button class="secondary">${loc}</button></a>`;
        }).join(" ");
    })();
    throw new Error("Missing location parameter"); // Halt execution
}

const appLocation = params.get("location");
substituteLocationString(appLocation);
document.getElementById("index-page").style.display = "none";
document.getElementById("app-page").style.display = "";

const filterDelay = 500;

function redGreenGradient(value, min, max) {
    const ratio = (value - min) / (max - min);
    return `rgba(${Math.round(255 * ratio)}, ${Math.round(255 * (1 - ratio))}, 0, 0.5)`;
}

// TODO: Optimise filter function (by only hiding/showing columns that have changed instead of all columns?)
function filterTable() {
    const filterValue = document.getElementById("filter").value.toLowerCase();
    [...document.getElementById("table-header").children].forEach((th, index) => {
        if (index <= 2) { // Do not filter ID, Last Updated, and Address columns
            return;
        }
        const visible = th.textContent.toLowerCase().includes(filterValue);
        th.style.display = visible ? "" : "none";
        document.querySelectorAll(`#table-body tr td:nth-child(${index + 1})`).forEach(td => {
            td.style.display = visible ? "" : "none";
        });
    });
}
document.getElementById("filter").addEventListener("input", () => {
    clearTimeout(filterTable.timeout);
    filterTable.timeout = setTimeout(filterTable, filterDelay);
});

// TODO: Add dictionary/object of restaurants instead of hardcoding
// TODO: Add support for switching languages (en-CA and fr-CA)
// TODO: Add gradiant colouring (red for expensive, green for cheap)
(async () => {
    const localization = Papa.parse(await fetch(`data/${appLocation}/localization.csv`).then(res => res.text()), { header: true }).data;
    const addresses = await fetch("addresses.json").then(res => res.json());

    let prices, tableHeader;
    const lang = document.documentElement.lang;

    if (lang === "en-CA") {
        prices = Papa.parse(await fetch(`data/${appLocation}/prices_en-CA.csv`).then(res => res.text()), { header: true }).data;
        tableHeader = ["ID", "Last Updated", "Address"];
    } else if (lang === "fr-CA") {
        prices = Papa.parse(await fetch(`data/${appLocation}/prices_fr-CA.csv`).then(res => res.text()), { header: true }).data;
        tableHeader = ["ID", "Mis à jour le", "Adresse"];
    } else {
        alert("Unsupported language: " + lang);
    }
    document.getElementById("total-restaurants").textContent = Object.keys(prices[0]).length - 1;

    const tableRows = [
        [["MIN", "#00000000"], ["N/A", "#00000000"], ["N/A", "#00000000"]],
        [["MAX", "#00000000"], ["N/A", "#00000000"], ["N/A", "#00000000"]],
        [["", "#00000000"]]
    ];
    Object.keys(prices[0]).forEach(key => {
        if (key === "any") {
            return;
        }
        tableRows.push([[key, "#00000000"], [addresses[key].updated || "N/A", "#00000000"], [addresses[key].addr || "N/A", "#00000000"]]);
    });

    prices.map((el, index) => {
        if (!el.any) {
            return;
        }
        const itemPrices = Object.values(el).filter(price => price !== "" && price !== "Y").map(price => parseInt(price));
        const minPrice = Math.min(...itemPrices);
        const maxPrice = Math.max(...itemPrices);
        if (minPrice === maxPrice) {
            return;
        }
        tableRows[0].push([(minPrice / 100).toFixed(2), redGreenGradient(minPrice, minPrice, maxPrice)]);
        tableRows[1].push([(maxPrice / 100).toFixed(2), redGreenGradient(maxPrice, minPrice, maxPrice)]);

        tableHeader.push(localization[index][lang]);
        tableRows.slice(3).forEach(row => {
            const price = el[row[0][0]] || "N/A";
            if (price === "N/A") {
                row.push(["N/A", "#00000000"]);
                return;
            }
            row.push([(price / 100).toFixed(2), redGreenGradient(price, minPrice, maxPrice)]);
        });
    });

    document.getElementById("table-header").innerHTML = tableHeader.map(header => `<th>${header}</th>`).join("");
    document.getElementById("table-body").innerHTML = tableRows.map(row => `<tr>${row.map(cell => {
        return `<td style="background-color: ${cell[1]}">${cell[0]}</td>`;
    }).join("")}</tr>`).join("");
    document.querySelectorAll("#table-body > tr:nth-child(n+3) > td:first-child").forEach(td => {
        td.innerHTML = `<a href="https://www.mcdonalds.com/ca/${lang.toLowerCase()}/location/${td.textContent}.html" target="_blank">${td.textContent}</a>`;
    });
})();