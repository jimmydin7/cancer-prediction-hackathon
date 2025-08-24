document.querySelectorAll('.scale-box').forEach(box => {
      box.addEventListener('click', () => {
        document.querySelectorAll('.scale-box').forEach(b => b.classList.remove('bg-blue-600', 'text-white'));
        box.classList.add('bg-blue-600', 'text-white');
        document.getElementById('scale-value').value = box.dataset.value;
      });
    });