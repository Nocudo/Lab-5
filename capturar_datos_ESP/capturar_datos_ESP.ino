const int pinR = 13; // Pines del LED RGB
const int pinG = 12;
const int pinB = 14;
const int pinLDR = 34; // Pin del LDR

void setup() {
  Serial.begin(115200);
  pinMode(pinR, OUTPUT);
  pinMode(pinG, OUTPUT);
  pinMode(pinB, OUTPUT);
  digitalWrite(pinR, LOW); // Asegurarnos de que el LED empiece apagado
  digitalWrite(pinG, LOW);
  digitalWrite(pinB, LOW);
}

void loop() {
  // Verificar si la computadora envio algun comando por el puerto serie
  if (Serial.available() > 0) {
    // Leer lo que llego hasta el salto de linea
    String comando = Serial.readStringUntil('\n');
    comando.trim(); // Eliminar espacios en blanco o retornos de carro invisibles
    if (comando == "CAPTURAR") {
      digitalWrite(pinR, HIGH); // 1. Leer Rojo
      delay(200); // Dar tiempo a que el LDR y la luz se estabilicen
      int valR = analogRead(pinLDR);
      digitalWrite(pinR, LOW);
      digitalWrite(pinG, HIGH); // 2. Leer Verde
      delay(200);
      int valG = analogRead(pinLDR);
      digitalWrite(pinG, LOW);
      digitalWrite(pinB, HIGH); // 3. Leer Azul
      delay(200);
      int valB = analogRead(pinLDR);
      digitalWrite(pinB, LOW);
      // Enviar datos por serial de vuelta a Python en formato: R,G,B
      Serial.print(valR);
      Serial.print(",");
      Serial.print(valG);
      Serial.print(",");
      Serial.println(valB);
    }
  }
}