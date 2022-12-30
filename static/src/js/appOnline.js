
/* Note : Cards variable is declared in cards.js file, which should be loaded before app.js"*/

var playCards;
var usedDeck = [];
var reader = new XMLHttpRequest() || new ActiveXObject('MSXML2.XMLHTTP');
var host = "https://cardx.vercel.app"
//var host = "http://localhost:3000"
var default_deck ="Demo Papo a Papo";
var deck = prompt("Qual o baralho a que quer aceder? Deixe em branco se quiser apenas espreitar");
var fetchURL = host+'/api/public/decks/'+ (deck ? deck : default_deck);


async function getcards (){
		// console.log(cards);
		  alert("Bem-vind@ ao Papo a Papo. Bom jogo!");
		var cardsapi;

		await fetch(fetchURL,{mode: 'cors'})
		  .then(response => response.json())
		  .then(data =>  cardsapi= data )
		  
		  mycards=cardsapi;

		  playCards = mycards;
		  startMeUp();
}
  
  getcards();




function startMeUp() {
  if (document.readyState == 'complete' ) {
    loadcard();
  } else {
    document.onreadystatechange = function () {
        if (document.readyState === "complete") {
          loadcard();
        }
    }
  }
}


/* from https://developer.mozilla.org/pt-BR/docs/Web/JavaScript/Reference/Global_Objects/Math/random*/
function getRandomInt(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min)) + min;
}

/* borrowed from https://www.htmlgoodies.com/beyond/javascript/article.php/3724571/Using-Multiple-JavaScript-Onload-Functions.htm*/

function loadcard() {

var ixcard;
if(playCards.length>1){ 
	ixcard = getRandomInt(0,playCards.length);
}
else {
	ixcard = getRandomInt(0,playCards.length-1);
}

var card;
let url="";
if (ixcard != undefined && ixcard != -1) {
	card = playCards[ixcard].cardText;
    url = playCards[ixcard].url;

      usedDeck.push(card);
      playCards.splice(ixcard,1);
}

      if(card == undefined) {
        card = "Chegou ao fim do baralho. Clique em Recomeçar para continuar"
		document.getElementById("main").innerHTML = ' <div class="card main"><div class="padTop"> '+ card + '</div></div>'
      }
      else if(url != undefined && url !="") {
		  document.getElementById("main").innerHTML = ' <div class="card main"> <img src="' + url + '" alt='+ card +' width="400" height="500"></div>' 
	  } 
	  else document.getElementById("main").innerHTML = ' <div class="card main"><div class="padTop"> '+ card + '</div></div>'

  /*   document.getElementById("main").innerHTML +=  '<div class="next" title="Próxima Carta" onclick="loadcard();"> Seguinte</div>'
     +'<div class="restart" title="Recomeçar" onclick="restart();"> Recomeçar</div>'
    */  
}

function restart(){
  
  getcards();
  usedDeck = [];
//  loadcard();
  
}
