const filterDelay = 500;

function redGreenGradient(value, min, max) {
    const ratio = (value - min) / (max - min);
    return `rgba(${Math.round(255 * ratio)}, ${Math.round(255 * (1 - ratio))}, 0, 0.5)`;
}

// TODO: Optimise filter function (by only hiding/showing columns that have changed instead of all columns?)
function filterTable() {
    const filterValue = document.getElementById("filter").value.toLowerCase();
    [...document.getElementById("table-header").children].forEach((th, index) => {
        if (index <= 1) {
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
    const localization = Papa.parse(await fetch("localization.csv").then(res => res.text()), { header: true }).data;
    const addresses = await fetch("addresses.json").then(res => res.json());

    let prices, tableHeader;
    const lang = document.documentElement.lang;

    if (lang === "en-CA") {
        prices = Papa.parse(await fetch("prices_en-CA.csv").then(res => res.text()), { header: true }).data;
        tableHeader = ["ID", "Address"];
    } else if (lang === "fr-CA") {
        prices = Papa.parse(await fetch("prices_fr-CA.csv").then(res => res.text()), { header: true }).data;
        tableHeader = ["ID", "Adresse"];
    } else {
        alert("Unsupported language: " + lang);
    }

    const tableRows = [];
    Object.keys(prices[0]).forEach(key => {
        if (key === "any") {
            return;
        }
        tableRows.push([[key, "#00000000"], [addresses[key] || "N/A", "#00000000"]]);
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

        tableHeader.push(localization[index][lang]);
        tableRows.forEach(row => {
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
})();