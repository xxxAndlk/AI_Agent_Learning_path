# PyTorch示例
@torch.no_grad()  # 禁用梯度计算，节省内存
def evaluate(model, data_loader):
    for batch in data_loader:
        output = model(batch)
    return output

# TensorFlow示例
@tf.function  # 将Python函数编译为计算图，加速执行
def train_step(images, labels):
    with tf.GradientTape() as tape:
        predictions = model(images)
        loss = loss_fn(labels, predictions)
    gradients = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    return loss
