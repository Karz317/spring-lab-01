package kz.iitu.springlab.notify;

public interface Notifier {

    String send(String message);

    String channel();
}
