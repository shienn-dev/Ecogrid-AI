async function calculateEnergy() {

    const power = document.getElementById("power").value;
    const hours = document.getElementById("hours").value;

    const response = await fetch(
        "http://127.0.0.1:5000/api/energy/calculate",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                power_watt: power,
                hours_per_day: hours
            })
        }
    );

    const data = await response.json();

    document.getElementById("result").innerHTML = `
        <p>Daily: ${data.daily_kwh} kWh</p>
        <p>Monthly: ${data.monthly_kwh} kWh</p>
        <p>Yearly: ${data.yearly_kwh} kWh</p>
    `;
}