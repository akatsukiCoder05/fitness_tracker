function calculateTDEE() {
    const age = parseFloat(document.getElementById('age').value);
    const gender = document.getElementById('gender').value;
    const height = parseFloat(document.getElementById('height').value);
    const weight = parseFloat(document.getElementById('weight').value);
    const activity = parseFloat(document.getElementById('activity').value);

    if (!age || !height || !weight) {
        alert("Please fill in all fields!");
        return;
    }

    // Calculate BMR (Basal Metabolic Rate)
    let bmr;
    if (gender === 'male') {
        bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age);
    } else {
        bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age);
    }

    // Calculate TDEE
    const tdee = bmr * activity;

    // Display Result
    document.getElementById('result').innerHTML = 
        `🔥 Your Total Daily Energy Expenditure (TDEE) is: <b>${tdee.toFixed(0)} calories/day</b>`;
}
