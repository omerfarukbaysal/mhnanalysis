window.Parsley.addValidator('palindrome', {
  validateString: function(value) {
    return value.split('').reverse().join('') === value;
  },
  messages: {
    en: 'This string is not the reverse of itself',
    fr: "Cette valeur n'est pas l'inverse d'elle même."
  }
});
