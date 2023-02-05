/* global NRDB, Promise, _ */

Promise.all([NRDB.data.promise, NRDB.ui.promise]).then(function() {
  // TODO(plural): Find a better place for this and remove the duplicate definitions.
  // This will filter matchingCards to only the latest version of each card, preserving the original order of matchingCards.
  function select_only_latest_cards(matchingCards) {
      var latestCardsByTitle = {};
      for (var card of matchingCards) {
          var latestCard = latestCardsByTitle[card.title];
          if (!latestCard || card.code > latestCard.code) {
              latestCardsByTitle[card.title] = card;
          }
      }
      return matchingCards.filter(function(value, index, arr) {
          return value.code == latestCardsByTitle[value.title].code;
      });
  }

  // We only need to calculate the latest_cards once and not on every findMatches call.
  var latest_cards = select_only_latest_cards(NRDB.data.cards.find());

  function findMatches(q, cb) {
    if (q.match(/^\w:/)) { return; }

    var regexp = new RegExp(q, 'i');
    function normalizeTitle(cardTitle) {
      return _.deburr(cardTitle).toLowerCase().trim();
    }
    var matchingCards = _.filter(latest_cards, function (card) {
      return regexp.test(normalizeTitle(card.title));
    });
    matchingCards.sort((card1, card2) => {
        var card1title = normalizeTitle(card1.title);
        var card2title = normalizeTitle(card2.title);
        var normalizedQuery = normalizeTitle(q);
        if(card1title.startsWith(normalizedQuery) && !card2title.startsWith(normalizedQuery)) {
            return -1;
        }
        if(card2title.startsWith(normalizedQuery) && !card1title.startsWith(normalizedQuery)) {
            return 1;
        }
        return card1.title < card2.title ? -1 : 1;
    });
    cb(matchingCards);
  }
  $('#top_nav_card_search_menu').on('shown.bs.dropdown', function (element) {
    $("#top_nav_card_search").focus();
  });

  $('#top_nav_card_search').typeahead({
    hint: true,
    highlight: true,
    minLength: 2
  }, {
    display: function(card) { return card.title + ' (' + card.pack.name + ')'; },
    source: findMatches
  });
  $('#top_nav_card_search').on('typeahead:selected typeahead:autocomplete', function(event, data) {
    location.href=Routing.generate('cards_zoom', {card_code:data.code, _locale:NRDB.locale});
  });

  $('#top_nav_card_search').keypress(function(event) {
    var keycode = (event.keyCode ? event.keyCode : event.which);
    if(keycode == '13'){
      $('#top_nav_card_search_form').submit();
    }
  });
});
