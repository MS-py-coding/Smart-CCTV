int pirPin = 2;
int ledPin = 13;
int pirState = LOW;
int val = 0;

unsigned long motionStart = 0;
unsigned long motionEnd = 0;

void setup() {
  pinMode(pirPin, INPUT);
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  Serial.println("PIR sensor test started...");
}

void loop() {
  val = digitalRead(pirPin);

  if (val == HIGH) {
    digitalWrite(ledPin, HIGH);
    if (pirState == LOW) {
      motionStart = millis();
      Serial.println("MOTION");
      pirState = HIGH;
    }
  } else {
    digitalWrite(ledPin, LOW);
    if (pirState == HIGH) {
      motionEnd = millis();
      unsigned long duration = (motionEnd - motionStart) / 1000;
      Serial.print("Motion ended! Duration: ");
      Serial.print(duration);
      Serial.println(" seconds.");
      pirState = LOW;
    }
  }
}