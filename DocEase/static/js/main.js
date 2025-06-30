document.addEventListener('DOMContentLoaded', function() {
    // --- File Converter Tabs ---
    const tabPdf = document.getElementById('tab-pdf-to-word');
    const tabWord = document.getElementById('tab-word-to-pdf');
    const tabImage = document.getElementById('tab-image-to-pdf');
    const contentPdf = document.getElementById('content-pdf-to-word');
    const contentWord = document.getElementById('content-word-to-pdf');
    const contentImage = document.getElementById('content-image-to-pdf');

    if (tabPdf && tabWord && tabImage && contentPdf && contentWord && contentImage) {
        tabPdf.addEventListener('click', function() {
            setActiveTab(tabPdf, [tabWord, tabImage]);
            showContent(contentPdf, [contentWord, contentImage]);
        });
        tabWord.addEventListener('click', function() {
            setActiveTab(tabWord, [tabPdf, tabImage]);
            showContent(contentWord, [contentPdf, contentImage]);
        });
        tabImage.addEventListener('click', function() {
            setActiveTab(tabImage, [tabPdf, tabWord]);
            showContent(contentImage, [contentPdf, contentWord]);
        });
    }

    // --- PDF Editor Buttons ---
    const btnSplit = document.getElementById('btn-split');
    const btnMerge = document.getElementById('btn-merge');
    const contentSplit = document.getElementById('content-split');
    const contentMerge = document.getElementById('content-merge');

    if (btnSplit && btnMerge && contentSplit && contentMerge) {
        btnSplit.addEventListener('click', function() {
            btnSplit.classList.add('active');
            btnMerge.classList.remove('active');
            contentSplit.style.display = '';
            contentMerge.style.display = 'none';
        });
        btnMerge.addEventListener('click', function() {
            btnSplit.classList.remove('active');
            btnMerge.classList.add('active');
            contentSplit.style.display = 'none';
            contentMerge.style.display = '';
        });
    }

    function setActiveTab(activeTab, inactiveTabs) {
        activeTab.classList.add('active');
        inactiveTabs.forEach(tab => tab.classList.remove('active'));
    }

    function showContent(activeContent, inactiveContents) {
        activeContent.style.display = '';
        inactiveContents.forEach(content => content.style.display = 'none');
    }

    // GSAP animation for card
    if (typeof gsap !== 'undefined') {
        gsap.from('.card-glass', {
            y: 40,
            opacity: 0,
            duration: 1,
            ease: 'power3.out'
        });
    }
});
