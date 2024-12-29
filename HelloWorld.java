public class TestClass {
    private String greeting;

    public TestClass(String greeting) {
        this.greeting = greeting;
    }

    public void sayHello() {
        System.out.println(greeting);
    }

    public static void main(String[] args) {
        TestClass hw = new TestClass("Hello, World!");
        hw.sayHello();
    }
}
