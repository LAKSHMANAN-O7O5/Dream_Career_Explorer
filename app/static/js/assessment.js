// --- Assessment Wizard Controller ---

document.addEventListener('DOMContentLoaded', () => {
    const quizForm = document.getElementById('quiz-form');
    if (!quizForm) return; // Exit if not on assessment page

    const steps = [...document.querySelectorAll('.quiz-step')];
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const progressNode = document.getElementById('step-progress');
    const stepNodes = document.querySelectorAll('.step-node');
    
    let currentStep = 0;
    const totalSteps = steps.length;

    // Initialize View
    showStep(currentStep);

    // Event listener for Next
    nextBtn.addEventListener("click", function () {

    if (!validateStep(currentStep)) {
        alert("Please answer all questions before continuing.");
        return;
    }

    if (currentStep < totalSteps - 1) {

        currentStep++;
        showStep(currentStep);

    } else {

        quizForm.submit();

    }

});

    // Event listener for Prev
    prevBtn.addEventListener('click', () => {
        if (currentStep > 0) {
            currentStep--;
            console.log(steps.length);
            console.log(currentStep);
            showStep(currentStep);
        }
    });

    function showStep(stepIndex) {
        steps.forEach((step, idx) => {
            if (idx === stepIndex) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });

        // Update Buttons
        if (stepIndex === 0) {
            prevBtn.style.visibility = 'hidden';
        } else {
            prevBtn.style.visibility = 'visible';
        }

        if (stepIndex === totalSteps - 1) {
            nextBtn.innerHTML = 'Submit Quiz <i class="fas fa-check-circle ms-2"></i>';
            nextBtn.classList.replace('btn-primary', 'btn-success');
        } else {
            nextBtn.innerHTML = 'Next Section <i class="fas fa-arrow-right ms-2"></i>';
            nextBtn.classList.replace('btn-success', 'btn-primary');
        }

        // Update Progress Bar
        const pct = (stepIndex / (totalSteps - 1)) * 100;
        if (progressNode) {
            progressNode.style.width = `${pct}%`;
        }

        // Update Step Nodes
        stepNodes.forEach((node, idx) => {
            const nodeIndex = parseInt(node.getAttribute('data-step'));
            if (nodeIndex === stepIndex) {
                node.className = 'step-node active';
            } else if (nodeIndex < stepIndex) {
                node.className = 'step-node completed';
                node.innerHTML = '<i class="fas fa-check"></i>';
            } else {
                node.className = 'step-node';
                node.innerHTML = nodeIndex + 1;
            }
        });

        // Scroll to top of assessment panel
        document.getElementById('assessment-wizard-card').scrollIntoView({ behavior: 'smooth' });
    }

   function validateStep(stepIndex) {

    const steps = document.querySelectorAll(".quiz-step");

    if (steps.length === 0) {
        console.log("No quiz steps found");
        return false;
    }

    if (stepIndex < 0 || stepIndex >= steps.length) {
        console.log("Invalid Step Index:", stepIndex);
        return false;
    }

    const currentStep = steps[stepIndex];

    if (!currentStep) {
        console.log("Current step undefined");
        return false;
    }

    const questions = currentStep.querySelectorAll(".question-wrapper");

    let valid = true;

    questions.forEach(question => {

        const checked = question.querySelector(
            "input[type='radio']:checked"
        );

        if (!checked) {
    valid = false;
    question.style.border = "2px solid #dc3545";
    question.style.backgroundColor = "rgba(220,53,69,0.08)";
} else {
    question.style.border = "1px solid var(--border-color)";
    question.style.backgroundColor = "";
}

    });

    if (!valid) {
    alert("Please answer all questions in this section.");
}

return valid;
}
});
