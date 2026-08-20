const form = document.getElementById("pledgeForm");
const pledgeIdInput = document.getElementById("pledgeId");
const formTitle = document.getElementById("formTitle");
const calculateBtn = document.getElementById("calculateBtn");
const saveBtn = document.getElementById("saveBtn");
const cancelEditBtn = document.getElementById("cancelEditBtn");
const refreshBtn = document.getElementById("refreshBtn");
const messageBox = document.getElementById("messageBox");
const calculationResult = document.getElementById("calculationResult");
const pledgeTableBody = document.getElementById("pledgeTableBody");
const recordCount = document.getElementById("recordCount");

const fields = {
    customerName: document.getElementById("customerName"),
    customerPhone: document.getElementById("customerPhone"),
    customerAddress: document.getElementById("customerAddress"),
    jewelleryType: document.getElementById("jewelleryType"),
    jewelleryWeight: document.getElementById("jewelleryWeight"),
    jewelleryPurity: document.getElementById("jewelleryPurity"),
    jewelleryDescription: document.getElementById("jewelleryDescription"),
    loanAmount: document.getElementById("loanAmount"),
    interestRate: document.getElementById("interestRate"),
    pledgeDate: document.getElementById("pledgeDate"),
    returnDate: document.getElementById("returnDate"),
};

const resultFields = {
    days: document.getElementById("resultDays"),
    perDay: document.getElementById("resultPerDay"),
    interest: document.getElementById("resultInterest"),
    final: document.getElementById("resultFinal"),
};

function formatCurrency(value) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        minimumFractionDigits: 2,
    }).format(value);
}

function showMessage(text, type = "success") {
    messageBox.textContent = text;
    messageBox.className = `message ${type}`;
    messageBox.classList.remove("hidden");
}

function hideMessage() {
    messageBox.classList.add("hidden");
}

function getFormData() {
    return {
        customer_name: fields.customerName.value.trim(),
        customer_phone: fields.customerPhone.value.trim(),
        customer_address: fields.customerAddress.value.trim(),
        jewellery_type: fields.jewelleryType.value.trim(),
        jewellery_weight: parseFloat(fields.jewelleryWeight.value),
        jewellery_purity: fields.jewelleryPurity.value.trim(),
        jewellery_description: fields.jewelleryDescription.value.trim(),
        loan_amount: parseFloat(fields.loanAmount.value),
        interest_rate: parseFloat(fields.interestRate.value),
        pledge_date: fields.pledgeDate.value,
        return_date: fields.returnDate.value,
    };
}

function displayCalculation(result) {
    resultFields.days.textContent = result.total_days;
    resultFields.perDay.textContent = formatCurrency(result.per_day_interest);
    resultFields.interest.textContent = formatCurrency(result.total_interest);
    resultFields.final.textContent = formatCurrency(result.final_amount);
    calculationResult.classList.remove("hidden");
}

async function calculateInterest() {
    hideMessage();

    const payload = getFormData();
    if (!payload.loan_amount || !payload.interest_rate || !payload.pledge_date || !payload.return_date) {
        showMessage("Please fill loan amount, interest rate, and both dates before calculating.", "error");
        return;
    }

    try {
        const response = await fetch("/api/calculate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Calculation failed.");
        }

        displayCalculation(data);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

function resetForm() {
    form.reset();
    pledgeIdInput.value = "";
    formTitle.textContent = "New Pledge Entry";
    saveBtn.textContent = "Save Pledge";
    cancelEditBtn.classList.add("hidden");
    calculationResult.classList.add("hidden");
    fields.interestRate.value = "7";
    setDefaultDates();
    hideMessage();
}

function setDefaultDates() {
    const today = new Date().toISOString().split("T")[0];
    fields.pledgeDate.value = today;
    fields.returnDate.value = today;
}

function renderPledges(pledges) {
    recordCount.textContent = `${pledges.length} record${pledges.length === 1 ? "" : "s"}`;

    if (!pledges.length) {
        pledgeTableBody.innerHTML = `
            <tr>
                <td colspan="10" class="empty-state">No pledge records found.</td>
            </tr>
        `;
        return;
    }

    pledgeTableBody.innerHTML = pledges
        .map(
            (pledge) => `
            <tr>
                <td data-label="ID">#${pledge.id}</td>
                <td data-label="Customer">
                    <strong>${pledge.customer_name}</strong><br>
                    <small>${pledge.customer_phone}</small>
                </td>
                <td data-label="Jewellery">
                    ${pledge.jewellery_type}<br>
                    <small>${pledge.jewellery_weight} g${pledge.jewellery_purity ? ` • ${pledge.jewellery_purity}` : ""}</small>
                </td>
                <td data-label="Loan">${formatCurrency(pledge.loan_amount)}</td>
                <td data-label="Rate">${pledge.interest_rate}%</td>
                <td data-label="Days">${pledge.total_days}</td>
                <td data-label="Interest">${formatCurrency(pledge.total_interest)}</td>
                <td data-label="Final Amount"><strong>${formatCurrency(pledge.final_amount)}</strong></td>
                <td data-label="Status"><span class="status ${pledge.status}">${pledge.status}</span></td>
                <td data-label="Actions">
                    <div class="table-actions">
                        <button class="link-btn" data-action="edit" data-id="${pledge.id}">Edit</button>
                        <button class="link-btn danger" data-action="delete" data-id="${pledge.id}">Delete</button>
                    </div>
                </td>
            </tr>
        `
        )
        .join("");
}

async function loadPledges() {
    try {
        const response = await fetch("/api/pledges");
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to load records.");
        }

        renderPledges(data);
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function savePledge(event) {
    event.preventDefault();
    hideMessage();

    const payload = getFormData();
    const pledgeId = pledgeIdInput.value;
    const isEdit = Boolean(pledgeId);

    try {
        const response = await fetch(isEdit ? `/api/pledges/${pledgeId}` : "/api/pledges", {
            method: isEdit ? "PUT" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to save pledge.");
        }

        displayCalculation(data);
        showMessage(data.message || "Pledge saved successfully.");
        resetForm();
        await loadPledges();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function editPledge(id) {
    try {
        const response = await fetch(`/api/pledges/${id}`);
        const pledge = await response.json();

        if (!response.ok) {
            throw new Error(pledge.error || "Unable to load pledge.");
        }

        pledgeIdInput.value = pledge.id;
        fields.customerName.value = pledge.customer_name;
        fields.customerPhone.value = pledge.customer_phone;
        fields.customerAddress.value = pledge.customer_address || "";
        fields.jewelleryType.value = pledge.jewellery_type;
        fields.jewelleryWeight.value = pledge.jewellery_weight;
        fields.jewelleryPurity.value = pledge.jewellery_purity || "";
        fields.jewelleryDescription.value = pledge.jewellery_description || "";
        fields.loanAmount.value = pledge.loan_amount;
        fields.interestRate.value = pledge.interest_rate;
        fields.pledgeDate.value = pledge.pledge_date;
        fields.returnDate.value = pledge.return_date;

        formTitle.textContent = `Edit Pledge #${pledge.id}`;
        saveBtn.textContent = "Update Pledge";
        cancelEditBtn.classList.remove("hidden");
        displayCalculation(pledge);
        window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (error) {
        showMessage(error.message, "error");
    }
}

async function deletePledge(id) {
    if (!window.confirm("Are you sure you want to delete this pledge record?")) {
        return;
    }

    try {
        const response = await fetch(`/api/pledges/${id}`, { method: "DELETE" });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to delete pledge.");
        }

        showMessage(data.message || "Pledge deleted successfully.");
        await loadPledges();
    } catch (error) {
        showMessage(error.message, "error");
    }
}

calculateBtn.addEventListener("click", calculateInterest);
form.addEventListener("submit", savePledge);
refreshBtn.addEventListener("click", loadPledges);
cancelEditBtn.addEventListener("click", resetForm);

pledgeTableBody.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) {
        return;
    }

    const id = button.dataset.id;
    if (button.dataset.action === "edit") {
        editPledge(id);
    } else if (button.dataset.action === "delete") {
        deletePledge(id);
    }
});

setDefaultDates();
loadPledges();
