document.addEventListener('DOMContentLoaded', function () {
    function getCsrfToken() {
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? match[1] : '';
    }

    // Rating stars logic
    const starsContainer = document.querySelector('.rating-section');
    if (starsContainer) {
        const tmdbId = starsContainer.dataset.tmdbId;
        const stars = starsContainer.querySelectorAll('.star');
        let saved = parseInt(starsContainer.dataset.saved || '0');

        stars.forEach(star => {
            star.addEventListener('mouseenter', function () {
                const val = parseInt(this.dataset.value);
                stars.forEach(s => {
                    s.classList.toggle('filled', parseInt(s.dataset.value) <= val);
                });
            });
            star.addEventListener('mouseleave', function () {
                stars.forEach(s => {
                    s.classList.toggle('filled', parseInt(s.dataset.value) <= saved);
                });
            });
            star.addEventListener('click', function () {
                const rating = parseInt(this.dataset.value);
                fetch(`/film/${tmdbId}/rate/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    },
                    body: JSON.stringify({ rating })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.ok) {
                        saved = rating;
                        starsContainer.dataset.saved = rating;
                        document.getElementById('avg-rating').textContent = data.avg;
                        stars.forEach(s => {
                            s.classList.toggle('filled', parseInt(s.dataset.value) <= saved);
                        });
                    }
                });
            });
        });
    }

    // Comment form logic
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const textarea = document.getElementById('comment-text');
            const text = textarea.value.trim();
            if (!text) return;
            const tmdbId = document.querySelector('.rating-section').dataset.tmdbId;
            fetch(`/film/${tmdbId}/comment/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ text })
            })
            .then(res => res.json())
            .then(data => {
                if (data.ok) {
                    const commentDiv = document.createElement('div');
                    commentDiv.className = 'comment';
                    commentDiv.innerHTML = `<strong>${data.user}</strong> <span class="comment-date">${data.date}</span><div>${data.text}</div>`;
                    const list = document.getElementById('comments-list');
                    list.prepend(commentDiv);
                    textarea.value = '';
                }
            });
        });
    }
});
