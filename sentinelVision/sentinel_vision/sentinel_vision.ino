const int buzzerPin = 13;
const int ledVerte = 12;
const int ledRouge = 11;

void setup() {
  pinMode(buzzerPin, OUTPUT);
  pinMode(ledVerte, OUTPUT);
  pinMode(ledRouge, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char commande = Serial.read();

    // SIGNAL D'ALERTE (Inconnu)
    if (commande == 'A') { 
      digitalWrite(ledRouge, HIGH);
      digitalWrite(buzzerPin, HIGH);
      delay(5000); // Buzz et LED Rouge pendant 5 secondes
      digitalWrite(buzzerPin, LOW);
      digitalWrite(ledRouge, LOW);
    }

    // SIGNAL D'ACCÈS (Connu)
    if (commande == 'V') { 
      digitalWrite(ledVerte, HIGH);
      delay(3000); // LED Verte pendant 3 secondes
      digitalWrite(ledVerte, LOW);
    }
  }
}