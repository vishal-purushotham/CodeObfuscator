public class HelloWorld {
    private String greeting;

    public HelloWorld(String greeting) {
        this.greeting = greeting;
    }

    public void sayHello() {
        System.out.println(greeting);
    }

    public static void main(String[] args) {
        HelloWorld hw = new HelloWorld("Hello, World!");
        hw.sayHello();
    }
}
